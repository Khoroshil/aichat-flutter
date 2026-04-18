import flet as ft
import json
import os

# Путь к файлу с настройками
SETTINGS_FILE = "settings.json"


def load_settings():
    """Загружает настройки из JSON файла"""
    try:
        if os.path.exists(SETTINGS_FILE):
            with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
    except:
        pass
    return {}


def save_settings(settings_dict):
    """Сохраняет настройки в JSON файл"""
    try:
        with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(settings_dict, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"Ошибка сохранения: {e}")
        return False


def settings_controls(page, navigate):
    
    # Загружаем сохранённые настройки
    saved = load_settings()
    
    # Поля ввода
    provider = ft.Dropdown(
        options=[
            ft.dropdown.Option("openrouter", "OpenRouter"),
            ft.dropdown.Option("vsegpt", "VseGPT"),
        ],
        label="Провайдер",
        value=saved.get("provider", "openrouter"),
        width=300
    )
    
    api_key = ft.TextField(
        label="API Key",
        password=True,
        can_reveal_password=True,
        value=saved.get("api_key", ""),
        width=400
    )
    
    # Дополнительные настройки модели
    temperature = ft.Slider(
        min=0.0,
        max=2.0,
        divisions=20,
        label="Temperature: {value}",
        value=saved.get("temperature", 0.7)
    )
    
    max_tokens = ft.Dropdown(
        options=[
            ft.dropdown.Option("512"),
            ft.dropdown.Option("1024"),
            ft.dropdown.Option("2048"),
            ft.dropdown.Option("4096"),
        ],
        label="Max Tokens",
        value=saved.get("max_tokens", "2048"),
        width=200
    )
    
    status_text = ft.Text("", size=14)
    
    def save_click(e):
        # Собираем настройки в словарь
        settings = {
            "provider": provider.value,
            "api_key": api_key.value,
            "temperature": temperature.value,
            "max_tokens": max_tokens.value
        }
        
        # Сохраняем в файл
        if save_settings(settings):
            status_text.value = "✅ Настройки сохранены!"
            status_text.color = ft.Colors.GREEN
        else:
            status_text.value = "❌ Ошибка сохранения!"
            status_text.color = ft.Colors.RED
        
        page.update()
    
    def test_connection(e):
        """Проверка API ключа"""
        if not api_key.value:
            status_text.value = "❌ Введите API ключ!"
            status_text.color = ft.Colors.RED
        else:
            status_text.value = "🔄 Проверка соединения..."
            status_text.color = ft.Colors.BLUE
            # Здесь потом будет реальная проверка API
        page.update()
    
    return [
        ft.Text("⚙️ Настройки", size=30, weight=ft.FontWeight.BOLD),
        
        ft.Divider(height=20),
        
        ft.Text("Провайдер API", size=18, weight=ft.FontWeight.W_500),
        provider,
        
        ft.Divider(height=20),
        
        ft.Text("API Ключ", size=18, weight=ft.FontWeight.W_500),
        api_key,
        ft.Row([
            ft.ElevatedButton("💾 Сохранить", on_click=save_click),
            ft.OutlinedButton("🔌 Проверить", on_click=test_connection),
        ]),
        
        ft.Divider(height=20),
        
        ft.Text("Параметры модели", size=18, weight=ft.FontWeight.W_500),
        ft.Text("Temperature (креативность)", size=14),
        temperature,
        ft.Text("Максимальное количество токенов", size=14),
        max_tokens,
        
        ft.Divider(height=20),
        
        status_text,
        
        ft.Divider(height=30),
        
        ft.ElevatedButton("← Назад", on_click=lambda e: navigate("home")),
    ]