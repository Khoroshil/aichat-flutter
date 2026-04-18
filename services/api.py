import requests
import json
import os
from datetime import datetime  # ← ВОТ ЭТО ДОБАВЬ

# Файл для хранения статистики
STATS_FILE = "stats.json"


def load_stats():
    """Загружает статистику использования"""
    try:
        if os.path.exists(STATS_FILE):
            with open(STATS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
    except:
        pass
    return {"total_tokens": 0, "history": [], "daily_expenses": {}, "model_stats": {}}


def save_stats(stats):
    """Сохраняет статистику"""
    try:
        with open(STATS_FILE, "w", encoding="utf-8") as f:
            json.dump(stats, f, ensure_ascii=False, indent=2)
        return True
    except:
        return False


def load_api_settings():
    """Загружает настройки API из settings.json"""
    try:
        if os.path.exists("settings.json"):
            with open("settings.json", "r", encoding="utf-8") as f:
                return json.load(f)
    except:
        pass
    return {}


def send_message_to_openrouter(message, api_key, model="openai/gpt-3.5-turbo", temperature=0.7, max_tokens=2048):
    """Отправляет запрос к OpenRouter API"""
    
    url = "https://openrouter.ai/api/v1/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost",
        "X-Title": "AI Chat App"
    }
    
    data = {
        "model": model,
        "messages": [{"role": "user", "content": message}],
        "temperature": temperature,
        "max_tokens": max_tokens
    }
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=30)
        response.raise_for_status()
        result = response.json()
        
        # Извлекаем ответ и статистику
        reply = result["choices"][0]["message"]["content"]
        tokens_used = result.get("usage", {}).get("total_tokens", 0)
        
        # Сохраняем статистику
        save_usage_stats(tokens_used, model)
        
        return {"success": True, "reply": reply, "tokens": tokens_used}
        
    except requests.exceptions.RequestException as e:
        return {"success": False, "error": f"Ошибка соединения: {str(e)}"}
    except KeyError as e:
        return {"success": False, "error": f"Ошибка ответа API: {str(e)}"}
    except Exception as e:
        return {"success": False, "error": f"Неизвестная ошибка: {str(e)}"}


def save_usage_stats(tokens_used, model):
    """Сохраняет статистику использования токенов"""
    stats = load_stats()
    
    # Обновляем общее количество токенов
    stats["total_tokens"] = stats.get("total_tokens", 0) + tokens_used
    
    # Статистика по моделям
    if "model_stats" not in stats:
        stats["model_stats"] = {}
    
    if model not in stats["model_stats"]:
        stats["model_stats"][model] = {
            "tokens": 0,
            "requests": 0,
            "cost": 0
        }
    
    stats["model_stats"][model]["tokens"] += tokens_used
    stats["model_stats"][model]["requests"] += 1
    
    # Примерная стоимость (разная для разных моделей)
    cost_per_1k = {
        "openai/gpt-3.5-turbo": 0.001,
        "openai/gpt-4": 0.03,
        "anthropic/claude-3-haiku": 0.00025,
        "google/gemini-pro": 0.000125,
    }
    
    cost = tokens_used * (cost_per_1k.get(model, 0.001) / 1000)
    stats["model_stats"][model]["cost"] += cost
    
    # Добавляем запись в историю
    today = datetime.now().strftime("%Y-%m-%d")
    stats["history"].append({
        "date": today,
        "tokens": tokens_used,
        "model": model,
        "timestamp": datetime.now().isoformat()
    })
    
    # Обновляем расходы по дням
    if today not in stats["daily_expenses"]:
        stats["daily_expenses"][today] = 0
    stats["daily_expenses"][today] += cost
    
    save_stats(stats)