import flet as ft
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
import io
import base64
from services.api import load_stats
from datetime import datetime, timedelta
import os


def create_expenses_chart(daily_expenses, days=7):
    """Создаёт график расходов по дням и сохраняет в файл"""
    
    if not daily_expenses:
        return None
    
    dates = []
    costs = []
    
    today = datetime.now().date()
    for i in range(days - 1, -1, -1):
        date = today - timedelta(days=i)
        date_str = date.strftime("%Y-%m-%d")
        dates.append(date.strftime("%d.%m"))
        costs.append(daily_expenses.get(date_str, 0))
    
    if sum(costs) == 0:
        return None
    
    fig, ax = plt.subplots(figsize=(8, 4))
    
    bars = ax.bar(dates, costs, color='#4CAF50', alpha=0.7, edgecolor='#2E7D32', linewidth=1)
    
    for bar, cost in zip(bars, costs):
        if cost > 0:
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(costs)*0.02,
                    f'${cost:.4f}', ha='center', va='bottom', fontsize=8)
    
    ax.set_title('Расходы по дням', fontsize=12, fontweight='bold')
    ax.set_xlabel('Дата', fontsize=10)
    ax.set_ylabel('Стоимость ($)', fontsize=10)
    ax.grid(axis='y', alpha=0.3, linestyle='--')
    ax.set_facecolor('#F5F5F5')
    fig.patch.set_facecolor('#FFFFFF')
    
    plt.tight_layout()
    
    chart_path = "expenses_chart.png"
    plt.savefig(chart_path, format='png', dpi=100, bbox_inches='tight')
    plt.close(fig)
    
    return chart_path


def expenses_controls(page, navigate):
    
    stats = load_stats()
    daily_expenses = stats.get("daily_expenses", {})
    model_stats = stats.get("model_stats", {})
    
    total_cost = sum(data["cost"] for data in model_stats.values())
    
    days_selector = ft.Dropdown(
        options=[
            ft.dropdown.Option("7", "7 дней"),
            ft.dropdown.Option("14", "14 дней"),
            ft.dropdown.Option("30", "30 дней"),
        ],
        value="7",
        width=150,
    )
    
    status_text = ft.Text("", color=ft.Colors.GREY_600)
    
    # Контейнер для контента
    chart_container = ft.Container(
        content=ft.Text(""),
        padding=10,
    )
    
    # Текст при отсутствии данных
    no_data_text = ft.Column([
        ft.Icon(ft.Icons.SHOW_CHART, size=64, color=ft.Colors.GREY_400),
        ft.Text("Нет данных о расходах", size=16, color=ft.Colors.GREY_600),
        ft.Text("Отправьте несколько сообщений в чате", size=14, color=ft.Colors.GREY_500),
        ft.ElevatedButton("💬 Перейти в чат", on_click=lambda e: navigate("home")),
    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)
    
    # Список расходов текстом
    expenses_list = ft.Column()
    
    def update_chart(e=None):
        days = int(days_selector.value)
        
        chart_container.content = None
        expenses_list.controls.clear()
        
        if daily_expenses:
            today = datetime.now().date()
            has_any = False
            
            for i in range(days - 1, -1, -1):
                date = today - timedelta(days=i)
                date_str = date.strftime("%Y-%m-%d")
                cost = daily_expenses.get(date_str, 0)
                
                if cost > 0:
                    has_any = True
                    expenses_list.controls.append(
                        ft.Row([
                            ft.Text(date.strftime("%d.%m.%Y"), width=120),
                            ft.Text(f"${cost:.6f}", weight=ft.FontWeight.BOLD, color=ft.Colors.GREEN_700),
                        ])
                    )
            
            if has_any:
                total_period = sum(daily_expenses.get((today - timedelta(days=i)).strftime('%Y-%m-%d'), 0) for i in range(days))
                chart_container.content = ft.Column([
                    ft.Text("📊 Расходы по дням:", size=16, weight=ft.FontWeight.W_500),
                    ft.Divider(height=10),
                    expenses_list,
                    ft.Divider(height=10),
                    ft.Text(f"💰 Всего за период: ${total_period:.6f}", 
                           size=14, weight=ft.FontWeight.BOLD),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)
                status_text.value = ""
            else:
                chart_container.content = no_data_text
                status_text.value = "Нет расходов за выбранный период"
        else:
            chart_container.content = no_data_text
            status_text.value = ""
        
        page.update()
    
    # Инициализация
    update_chart()
    
    total_card = ft.Card(
        content=ft.Container(
            content=ft.Column([
                ft.Text("Общие расходы", size=14, color=ft.Colors.GREY_700),
                ft.Text(f"${total_cost:.6f}", size=32, weight=ft.FontWeight.BOLD, color=ft.Colors.GREEN_800),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            padding=ft.padding.symmetric(horizontal=25, vertical=15),
        ),
    )
    
    return [
        ft.Text("📈 График расходов", size=28, weight=ft.FontWeight.BOLD),
        
        ft.Divider(height=10),
        
        ft.Row([
            total_card,
            ft.Container(width=15),
            ft.Column([
                ft.Text("Период:", size=12),
                ft.Row([
                    days_selector,
                    ft.IconButton(
                        icon=ft.Icons.REFRESH,
                        tooltip="Обновить",
                        on_click=update_chart,
                    ),
                ]),
            ]),
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
        
        ft.Divider(height=20),
        
        ft.Container(
            content=ft.Column([
                chart_container,
                status_text,
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            padding=15,
        ),
        
        ft.Divider(height=25),
        
        ft.Row([
            ft.ElevatedButton("← Назад", on_click=lambda e: navigate("home")),
            ft.ElevatedButton("📊 Статистика", on_click=lambda e: navigate("stats")),
        ]),
    ]