
import streamlit as st
import json
import os
from pathlib import Path

# Конфигурация
st.set_page_config(
    page_title="Hikka Module Control Panel",
    page_icon="🐮",
    layout="wide"
)

def get_base_dir():
    return Path(os.getenv("HIKKA_DIR", "/root/data"))

def get_config_path(user_id):
    base = get_base_dir()
    base.mkdir(parents=True, exist_ok=True)
    return base / f"config-{user_id}.json"

st.write(f"HOME={Path.home()}")
st.write(f"HIKKA_DIR={os.getenv('HIKKA_DIR')}")
p = get_config_path(user_id)
st.write(f"Config path={p}, exists={p.exists()}")

def load_config(user_id):
    config_path = get_config_path(user_id)
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        st.error(f"Конфиг не найден: {config_path}")
        return None
    except json.JSONDecodeError:
        st.error(f"Ошибка чтения JSON из {config_path}")
        return None

def save_config(user_id, config_data):
    config_path = get_config_path(user_id)
    try:
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, indent=4, ensure_ascii=False)
        return True
    except Exception as e:
        st.error(f"Ошибка сохранения: {e}")
        return False

# Главная страница
st.title("🐮 Hikka AutoFarmbot Control Panel")

# Сайдбар для ввода User ID
with st.sidebar:
    st.header("Настройки подключения")
    user_id = st.text_input(
        "User ID аккаунта",
        placeholder="123456789",
        help="Введите User ID вашего Telegram аккаунта"
    )

    if user_id:
        st.success(f"Подключение к конфигу: config-{user_id}.json")

    st.divider()
    st.markdown("### Информация")
    st.info("Этот веб-интерфейс позволяет управлять настройками модуля AutoFarmbot для Hikka")

# Основной контент
if user_id:
    config = load_config(user_id)

    if config:
        st.success("✅ Конфиг успешно загружен!")

        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "🌳 Автолес", 
            "🧤 Автокрафт", 
            "🥛 Автодойка",
            "🪴 Кактус",
            "⚙️ Общие настройки"
        ])

        with tab1:
            st.header("🌳 Настройки Автолеса")

            col1, col2 = st.columns(2)

            with col1:
                forest_enabled = st.checkbox(
                    "Включить автолес",
                    value=config.get("config_bot_auto_forest", False),
                    key="forest_enabled"
                )
                config["config_bot_auto_forest"] = forest_enabled

                skip_npc = st.checkbox(
                    "Скипать NPC",
                    value=config.get("config_bot_auto_forest_skip_npc", True),
                    key="skip_npc"
                )
                config["config_bot_auto_forest_skip_npc"] = skip_npc

            with col2:
                # Команды для запуска
                forest_commands = config.get("config_bot_auto_forest_command", ["мулс"])
                selected_cmd = st.selectbox(
                    "Команда запуска",
                    ["/forest", "мулс", "му лес"],
                    index=0 if not forest_commands else (
                        ["/forest", "мулс", "му лес"].index(forest_commands[0]) 
                        if forest_commands[0] in ["/forest", "мулс", "му лес"] 
                        else 0
                    )
                )
                config["config_bot_auto_forest_command"] = [selected_cmd]

            st.divider()
            st.subheader("🦔 Выбор NPC для пропуска")
            npc_list = {
                "npc_belka": "🐿 Белочка",
                "npc_jabomraz": "🐸 Жабомразь",
                "npc_edinorog": "🦄 Единорожка",
                "npc_djun": "🦜 Джун",
                "npc_chick": "🐤 Цыпа",
                "npc_bear": "🐻 Тэдди",
                "npc_ejik": "💕🦔 Винди"
            }

            current_npcs = config.get("config_bot_autoforest_npcs", [])

            cols = st.columns(3)
            for i, (npc_key, npc_name) in enumerate(npc_list.items()):
                with cols[i % 3]:
                    checked = st.checkbox(
                        npc_name,
                        value=npc_key in current_npcs,
                        key=f"npc_{npc_key}"
                    )
                    if checked and npc_key not in current_npcs:
                        current_npcs.append(npc_key)
                    elif not checked and npc_key in current_npcs:
                        current_npcs.remove(npc_key)

            config["config_bot_autoforest_npcs"] = current_npcs

        # Вкладка Автокрафт
        with tab2:
            st.header("🧤 Настройки Автокрафта")

            col1, col2 = st.columns(2)

            with col1:
                craft_enabled = st.checkbox(
                    "Включить автокрафт",
                    value=config.get("config_bot_auto_craft", False),
                    key="craft_enabled"
                )
                config["config_bot_auto_craft"] = craft_enabled

                craft_item = st.text_input(
                    "Название предмета",
                    value=config.get("config_bot_auto_craft_item_name", "масло"),
                    placeholder="масло, куки и т.д.",
                    key="craft_item"
                )
                config["config_bot_auto_craft_item_name"] = craft_item

            with col2:
                craft_count = st.number_input(
                    "Количество для крафта",
                    min_value=1,
                    max_value=100,
                    value=int(config.get("config_bot_auto_craft_count", 50)),
                    key="craft_count"
                )
                config["config_bot_auto_craft_count"] = str(craft_count)

                craft_command = st.selectbox(
                    "Команда запуска",
                    ["/craft", "мув", "му крафт"],
                    index=["/craft", "мув", "му крафт"].index(
                        config.get("config_bot_auto_craft_command", "мув")
                    ) if config.get("config_bot_auto_craft_command") in ["/craft", "мув", "му крафт"] else 1
                )
                config["config_bot_auto_craft_command"] = craft_command

        # Вкладка Автодойка
        with tab3:
            st.header("🥛 Настройки Автодойки")

            col1, col2 = st.columns(2)

            with col1:
                milk_enabled = st.checkbox(
                    "Включить автодойку",
                    value=config.get("config_bot_auto_milk", False),
                    key="milk_enabled"
                )
                config["config_bot_auto_milk"] = milk_enabled

            with col2:
                milk_commands = config.get("config_bot_auto_milk_command", ["мук"])
                milk_cmd = st.selectbox(
                    "Команда запуска",
                    ["/cow", "мук", "му корова"],
                    index=0 if not milk_commands else (
                        ["/cow", "мук", "му корова"].index(milk_commands[0])
                        if milk_commands[0] in ["/cow", "мук", "му корова"]
                        else 1
                    )
                )
                config["config_bot_auto_milk_command"] = [milk_cmd]

        # Вкладка Кактус
        with tab4:
            st.header("🪴 Настройки Кактуса")

            col1, col2 = st.columns(2)

            with col1:
                cactus_enabled = st.checkbox(
                    "Включить автокактус",
                    value=config.get("config_bot_auto_cactus", True),
                    key="cactus_enabled"
                )
                config["config_bot_auto_cactus"] = cactus_enabled

                water_enabled = st.checkbox(
                    "Поливать кактус",
                    value=config.get("config_bot_auto_cactus_water_drink", True),
                    key="water_enabled"
                )
                config["config_bot_auto_cactus_water_drink"] = water_enabled

            with col2:
                water_lvl = st.slider(
                    "Уровень воды для полива (%)",
                    min_value=0,
                    max_value=100,
                    value=int(config.get("config_bot_auto_cactus_water_drink_lvl", 50)),
                    key="water_lvl"
                )
                config["config_bot_auto_cactus_water_drink_lvl"] = str(water_lvl)

                water_clicks = st.number_input(
                    "Количество кликов полива",
                    min_value=1,
                    max_value=10,
                    value=int(config.get("config_bot_auto_cactus_water_drink_click", 1)),
                    help="1 клик = 50% воды",
                    key="water_clicks"
                )
                config["config_bot_auto_cactus_water_drink_click"] = str(water_clicks)

        # Вкладка Общие настройки
        with tab5:
            st.header("⚙️ Общие настройки")

            col1, col2 = st.columns(2)

            with col1:
                debug_enabled = st.checkbox(
                    "Режим отладки",
                    value=config.get("config_debug_msg", False),
                    key="debug_enabled"
                )
                config["config_debug_msg"] = debug_enabled

                chat_id = st.text_input(
                    "ID чата для работы",
                    value=str(config.get("config_bot_used_chat_id", "1606812809")),
                    placeholder="1606812809",
                    key="chat_id"
                )
                config["config_bot_used_chat_id"] = chat_id

            with col2:
                log_chat = st.text_input(
                    "Куда отправлять логи",
                    value=config.get("config_bot_send_logs", "me"),
                    placeholder="me, default или ID чата",
                    key="log_chat"
                )
                config["config_bot_send_logs"] = log_chat

                timezone = st.selectbox(
                    "Часовой пояс",
                    ["UTC", "Europe/Kiev", "Europe/Moscow", "Asia/Tokyo", "America/New_York", "Europe/London"],
                    index=["UTC", "Europe/Kiev", "Europe/Moscow", "Asia/Tokyo", "America/New_York", "Europe/London"].index(
                        config.get("config_user_tz", "UTC")
                    ) if config.get("config_user_tz") in ["UTC", "Europe/Kiev", "Europe/Moscow", "Asia/Tokyo", "America/New_York", "Europe/London"] else 0
                )
                config["config_user_tz"] = timezone

        # Кнопка сохранения
        st.divider()
        col1, col2, col3 = st.columns([1, 1, 2])

        with col1:
            if st.button("💾 Сохранить изменения", type="primary", use_container_width=True):
                if save_config(user_id, config):
                    st.success("✅ Конфигурация успешно сохранена!")
                    st.balloons()

        with col2:
            if st.button("🔄 Перезагрузить", use_container_width=True):
                st.rerun()

        # Показываем JSON конфиг
        with st.expander("📋 Просмотр JSON конфига"):
            st.json(config)

else:
    st.info("👈 Введите User ID в боковой панели для начала работы")

    st.markdown("""
    ### 📚 Как использовать:

    1. **Найдите ваш User ID** - это ID вашего Telegram аккаунта
    2. **Введите его** в поле слева
    3. **Конфиг будет автоматически загружен** из файла `config-{user_id}.json`
    4. **Настройте параметры** через удобный веб-интерфейс
    5. **Сохраните изменения** - они сразу применятся к модулю

    ### 📁 Расположение конфигов:

    По умолчанию конфиги Hikka находятся в:
    - **Linux/MacOS**: `~/Hikka/config-{user_id}.json`

    ### ⚠️ Важно:

    - Убедитесь, что путь к папке Hikka указан правильно
    - Модуль должен быть загружен в Hikka для применения настроек
    - После изменения конфига может потребоваться перезапуск модуля
    """, unsafe_allow_html=True)

# Футер
st.divider()
st.markdown("""
<div style='text-align: center; color: gray;'>
    <p>Hikka AutoFarmbot Control Panel v1.0</p>
    <p>Создано для управления модулем AutoFarmbot</p>
</div>
""", unsafe_allow_html=True)
