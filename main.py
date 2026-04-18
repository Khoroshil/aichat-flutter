import flet as ft

# Импортируем функции, которые возвращают КОНТРОЛЫ (не View)
from pages.home import home_controls
from pages.settings import settings_controls
from pages.stats import stats_controls
from pages.expenses import expenses_controls


def main(page: ft.Page):
    page.title = "AI Chat"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 20
    
    # Текущая страница
    current_page = "home"
    
    # Контейнер для контента
    content_container = ft.Column()
    
    def show_page(page_name):
        nonlocal current_page
        current_page = page_name
        
        # Очищаем контейнер
        content_container.controls.clear()
        
        # Добавляем нужные контролы
        if page_name == "home":
            content_container.controls.extend(home_controls(page, show_page))
        elif page_name == "settings":
            content_container.controls.extend(settings_controls(page, show_page))
        elif page_name == "stats":
            content_container.controls.extend(stats_controls(page, show_page))
        elif page_name == "expenses":
            content_container.controls.extend(expenses_controls(page, show_page))
        
        page.update()
    
    # Показываем главную страницу
    show_page("home")
    
    # Добавляем контейнер на страницу
    page.add(content_container)


ft.app(target=main)