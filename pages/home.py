import flet as ft
from services.api import send_message_to_openrouter, load_api_settings


def home_controls(page, navigate):
    
    # Загружаем настройки
    settings = load_api_settings()
    has_api_key = bool(settings.get("api_key"))
    
    # Поле ввода сообщения
    message_input = ft.TextField(
        label="Введите сообщение",
        multiline=True,
        min_lines=1,
        max_lines=5,
        width=500,
        disabled=not has_api_key
    )
    
    # Область чата
    chat_history = ft.Column(scroll=ft.ScrollMode.AUTO, height=400, width=600)
    
    # Статус
    status_text = ft.Text("")
    
    # Индикатор загрузки
    loading = ft.ProgressRing(visible=False, width=20, height=20)
    
    # Выбор модели
    model_dropdown = ft.Dropdown(
        options=[
            ft.dropdown.Option("openai/gpt-3.5-turbo", "GPT-3.5 Turbo"),
            ft.dropdown.Option("openai/gpt-4", "GPT-4"),
            ft.dropdown.Option("anthropic/claude-3-haiku", "Claude 3 Haiku"),
            ft.dropdown.Option("google/gemini-pro", "Gemini Pro"),
        ],
        label="Модель",
        value="openai/gpt-3.5-turbo",
        width=250,
        disabled=not has_api_key
    )
    
    def add_message(text, is_user=True):
        """Добавляет сообщение в чат"""
        align = ft.MainAxisAlignment.END if is_user else ft.MainAxisAlignment.START
        color = ft.Colors.BLUE_100 if is_user else ft.Colors.GREY_200
        icon = "👤" if is_user else "🤖"
        
        chat_history.controls.append(
            ft.Row([
                ft.Container(
                    content=ft.Column([
                        ft.Text(icon, size=16),
                        ft.Text(text, size=14),
                    ]),
                    bgcolor=color,
                    padding=10,
                    border_radius=10,
                )
            ], alignment=align)
        )
        page.update()
    
    def send_message(e):
        if not message_input.value:
            return
        
        user_message = message_input.value
        message_input.value = ""
        message_input.disabled = True
        loading.visible = True
        status_text.value = "🔄 Отправка..."
        page.update()
        
        # Добавляем сообщение пользователя
        add_message(user_message, is_user=True)
        
        # Загружаем свежие настройки
        settings = load_api_settings()
        api_key = settings.get("api_key", "")
        
        # Отправляем запрос
        result = send_message_to_openrouter(
            message=user_message,
            api_key=api_key,
            model=model_dropdown.value,
            temperature=settings.get("temperature", 0.7),
            max_tokens=int(settings.get("max_tokens", 2048))
        )
        
        if result["success"]:
            add_message(result["reply"], is_user=False)
            status_text.value = f"✅ Ответ получен (токенов: {result['tokens']})"
            status_text.color = ft.Colors.GREEN
        else:
            status_text.value = f"❌ {result['error']}"
            status_text.color = ft.Colors.RED
        
        message_input.disabled = False
        loading.visible = False
        page.update()
    
    def clear_chat(e):
        chat_history.controls.clear()
        status_text.value = ""
        page.update()
    
    # Предупреждение, если нет API ключа
    warning = ft.Container(
        content=ft.Row([
            ft.Icon(ft.Icons.WARNING, color=ft.Colors.ORANGE),
            ft.Text("API ключ не настроен!", size=14, color=ft.Colors.ORANGE),
            ft.TextButton("Настроить", on_click=lambda e: navigate("settings")),
        ]),
        visible=not has_api_key,
        bgcolor=ft.Colors.ORANGE_50,
        padding=10,
        border_radius=5,
    )
    
    return [
        ft.Text("💬 AI Чат", size=30, weight=ft.FontWeight.BOLD),
        
        warning,
        
        ft.Row([
            model_dropdown,
            ft.IconButton(
                icon=ft.Icons.DELETE,
                tooltip="Очистить чат",
                on_click=clear_chat,
            ),
        ]),
        
        chat_history,
        
        ft.Divider(height=10),
        
        ft.Row([
            message_input,
            ft.IconButton(
                icon=ft.Icons.SEND,
                tooltip="Отправить",
                on_click=send_message,
                disabled=not has_api_key,
            ),
            loading,
        ], alignment=ft.MainAxisAlignment.START),
        
        status_text,
        
        ft.Divider(height=20),
        
        ft.Row([
            ft.ElevatedButton("⚙️ Настройки", on_click=lambda e: navigate("settings")),
            ft.ElevatedButton("📊 Статистика", on_click=lambda e: navigate("stats")),
            ft.ElevatedButton("📈 Расходы", on_click=lambda e: navigate("expenses")),
        ]),
    ]