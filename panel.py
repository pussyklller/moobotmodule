# streamlit_app.py
import asyncio
import json
import streamlit as st
import redis.asyncio as aioredis

REDIS_URL = st.secrets.get("redis_url", "redis://default:a443832c5be67d49@192.168.1.100:6379/0")
USER_ID = st.secrets.get("user_id")
CHANNEL = "panel:cmd"

@st.cache_resource
def get_redis():
    return aioredis.from_url(REDIS_URL, encoding="utf-8", decode_responses=True)

redis = get_redis()

async def rpc_call(cmd: dict):
    corr = f"rpc:{cmd['op']}:{cmd.get('key','')}:{st.session_state.get('nonce', '0')}"
    await redis.publish(CHANNEL, json.dumps({"corr": corr, **cmd}))
    # panel:resp:{corr}

def ttl_to_str(ttl: int):
    if ttl <= 0:
        return "нет таймера"
    m, s = divmod(ttl, 60)
    return f"{m} мин {s} сек"

async def load_snapshot():
    snap_raw = await redis.get("panel:snapshot")
    return json.loads(snap_raw) if snap_raw else {}

def ui():
    st.title("🦌 Hikka AutoFarm — Панель")
    snap = asyncio.run(load_snapshot())

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Чат", snap.get("chat_id", "-"))
        st.write("Боты: " + ", ".join(snap.get("used_bots", [])))
    with col2:
        st.metric("Временная зона", snap.get("timezone", "UTC"))
    with col3:
        st.write("Команды:")
        st.code(snap.get("commands", {}))

    st.subheader("Таймеры")
    for k, ttl in (snap.get("timers") or {}).items():
        st.write(f"{k} → {ttl_to_str(ttl)}")

    st.subheader("Функции")
    feats = snap.get("features", {})
    c1, c2, c3 = st.columns(3)
    with c1:
        auto_craft = st.toggle("Автокрафт", feats.get("auto_craft", False))
        auto_forest = st.toggle("Автолес", feats.get("auto_forest", False))
    with c2:
        auto_milk = st.toggle("Автодойка", feats.get("auto_milk", False))
        auto_eat = st.toggle("Автоеда", feats.get("auto_eat", False))
    with c3:
        chick_house = st.toggle("Курятник", feats.get("chick_house", False))
        cactus = st.toggle("Кактус", feats.get("cactus", False))

    if st.button("Сохранить переключатели"):
        cfg = {
            "config_bot_auto_craft": auto_craft,
            "config_bot_auto_forest": auto_forest,
            "config_bot_auto_milk": auto_milk,
            "config_bot_auto_eat": auto_eat,
            "config_bot_auto_chick_house": chick_house,
            "config_bot_auto_cactus": cactus,
        }
        asyncio.run(rpc_call({"op": "set_config_bulk", "values": cfg}))
        st.success("Сохранено")

    st.subheader("Кактус")
    cactus_lvl = st.number_input("Порог воды (%)", 0, 100, int(snap.get("cactus", {}).get("water_level_threshold", 50)))
    cactus_clicks = st.number_input("Кликов waterup", 0, 50, int(snap.get("cactus", {}).get("water_clicks", 1)))
    ccol1, ccol2 = st.columns(2)
    if ccol1.button("Сохранить кактус"):
        asyncio.run(rpc_call({"op": "set_config_bulk", "values": {
            "config_bot_auto_cactus_water_drink_lvl": int(cactus_lvl),
            "config_bot_auto_cactus_water_drink_click": int(cactus_clicks),
        }}))
        st.success("Сохранено")
    if ccol2.button("Полить сейчас"):
        asyncio.run(rpc_call({"op": "action", "name": "cactus_water"}))
        st.info("Команда отправлена")

    st.subheader("Автокрафт")
    craft_item = st.text_input("Предмет", value="масло")
    craft_count = st.number_input("Количество", 1, 100, 50)
    ac1, ac2, ac3 = st.columns(3)
    if ac1.button("Сохранить крафт"):
        asyncio.run(rpc_call({"op": "set_config_bulk", "values": {
            "config_bot_auto_craft_item_name": craft_item,
            "config_bot_auto_craft_count": int(craft_count),
        }}))
        st.success("Сохранено")
    if ac2.button("Запустить крафт"):
        asyncio.run(rpc_call({"op": "action", "name": "start_craft"}))
        st.info("Команда отправлена")

    st.subheader("Курятник")
    chicks = st.number_input("Цыплят", 0, 1000, int(snap.get("config", {}).get("config_bot_auto_chick_house_chick_count", 0)))
    if st.button("Сохранить кол-во цып"):
        asyncio.run(rpc_call({"op": "set_config", "key": "config_bot_auto_chick_house_chick_count", "value": int(chicks)}))
        st.success("Сохранено")

    st.subheader("Логи")
    categories = st.multiselect("Категории", ["Redis","Forest","Eating","Crafting","State","General"], default=["General"])
    if st.button("Применить категории логов"):
        asyncio.run(rpc_call({"op": "set_config", "key": "config_debug_diff_msg", "value": categories}))
        asyncio.run(rpc_call({"op": "set_config", "key": "config_debug_msg", "value": True}))
        st.success("Категории обновлены, логирование включено")

if __name__ == "__main__":
    ui()
