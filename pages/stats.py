import flet as ft
from services.api import load_stats


def stats_controls(page, navigate):
    
    # Загружаем статистику
    stats = load_stats()
    total_tokens = stats.get("total_tokens", 0)
    model_stats = stats.get("model_stats", {})
    
    # Создаём строки таблицы для каждой модели
    table_rows = []
    
    for model, data in model_stats.items():
        # Красивое имя модели
        display_name = model.split("/")[-1].replace("-", " ").title()
        
        table_rows.append(
            ft.DataRow(cells=[
                ft.DataCell(ft.Text(display_name)),
                ft.DataCell(ft.Text(str(data["requests"]), text_align=ft.TextAlign.CENTER)),
                ft.DataCell(ft.Text(f"{data['tokens']:,}".replace(",", " "), text_align=ft.TextAlign.RIGHT)),
                ft.DataCell(ft.Text(f"${data['cost']:.4f}", text_align=ft.TextAlign.RIGHT)),
            ])
        )
    
    # Таблица статистики
    stats_table = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("Модель", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Запросов", weight=ft.FontWeight.BOLD), numeric=True),
            ft.DataColumn(ft.Text("Токенов", weight=ft.FontWeight.BOLD), numeric=True),
            ft.DataColumn(ft.Text("Стоимость", weight=ft.FontWeight.BOLD), numeric=True),
        ],
        rows=table_rows,
        border=ft.border.all(1, ft.Colors.GREY_300),
        border_radius=10,
        vertical_lines=ft.border.BorderSide(1, ft.Colors.GREY_200),
        horizontal_lines=ft.border.BorderSide(1, ft.Colors.GREY_200),
        sort_column_index=2,
        sort_ascending=False,
    )
    
    # Общая статистика
    total_cost = sum(data["cost"] for data in model_stats.values())
    total_requests = sum(data["requests"] for data in model_stats.values())
    
    # Карточки с общей информацией
    summary_cards = ft.Row([
        ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Text("Всего запросов", size=14, color=ft.Colors.GREY_700),
                    ft.Text(str(total_requests), size=32, weight=ft.FontWeight.BOLD),
                ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                padding=20,
                width=150,
            ),
        ),
        ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Text("Всего токенов", size=14, color=ft.Colors.GREY_700),
                    ft.Text(f"{total_tokens:,}".replace(",", " "), size=32, weight=ft.FontWeight.BOLD),
                ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                padding=20,
                width=180,
            ),
        ),
        ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Text("Общая стоимость", size=14, color=ft.Colors.GREY_700),
                    ft.Text(f"${total_cost:.4f}", size=32, weight=ft.FontWeight.BOLD),
                ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                padding=20,
                width=170,
            ),
        ),
    ], alignment=ft.MainAxisAlignment.SPACE_EVENLY)
    
    # Если нет данных
    if not model_stats:
        no_data = ft.Container(
            content=ft.Column([
                ft.Icon(ft.Icons.ANALYTICS, size=64, color=ft.Colors.GREY_400),
                ft.Text("Нет данных для отображения", size=16, color=ft.Colors.GREY_600),
                ft.Text("Отправьте сообщение в чате, чтобы увидеть статистику", size=14, color=ft.Colors.GREY_500),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            padding=40,
        )
        content = [no_data]
    else:
        content = [
            summary_cards,
            ft.Divider(height=30),
            ft.Text("Детализация по моделям", size=18, weight=ft.FontWeight.W_500),
            stats_table,
        ]
    
    return [
        ft.Text("📊 Статистика использования", size=30, weight=ft.FontWeight.BOLD),
        ft.Divider(height=20),
        *content,
        ft.Divider(height=30),
        ft.Row([
            ft.ElevatedButton("← Назад", on_click=lambda e: navigate("home")),
            ft.ElevatedButton("📈 Расходы", on_click=lambda e: navigate("expenses")),
        ]),
    ]