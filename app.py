import pymongo
from datetime import datetime
from dotenv import load_dotenv
import os
import json
from colorama import Fore, Style

# Завантаження конфігурації з .env
load_dotenv()
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")

# Підключення до MongoDB
try:
    client = pymongo.MongoClient(MONGO_URI)
    db = client["recipe_db"]  # Створення бази даних
    collection = db["recipes"]  # Створення колекції
    collection.create_index("name")  # Індексація для оптимізації пошуку
except pymongo.errors.ConnectionError as e:
    print(Fore.RED + "❌ Помилка з'єднання з MongoDB:" + Style.RESET_ALL, e)
    exit()

# CRUD-операції
def add_recipe():
    """Додає новий рецепт у базу даних."""
    try:
        name = input("Введіть назву рецепта: ")
        category = input("Категорія страви (суп, десерт тощо): ")
        time = input("Час приготування (хвилини): ")
        if not time.isdigit() or int(time) <= 0:
            print(Fore.RED + "❌ Введіть коректний час приготування!" + Style.RESET_ALL)
            return
        time = int(time)
        ingredients = input("Список інгредієнтів (через кому): ").split(", ")
        instructions = input("Опишіть процес приготування: ")

        recipe = {
            "name": name,
            "category": category,
            "time": time,
            "ingredients": ingredients,
            "instructions": instructions,
            "created_at": datetime.now()
        }
        collection.insert_one(recipe)
        print(Fore.GREEN + "✅ Рецепт успішно додано!" + Style.RESET_ALL)
    except Exception as e:
        print(Fore.RED + "❌ Помилка додавання рецепта:" + Style.RESET_ALL, e)

def view_recipes():
    """Перегляд усіх рецептів."""
    try:
        recipes = collection.find()
        for recipe in recipes:
            print(f"Назва: {recipe['name']}, Категорія: {recipe['category']}, Час: {recipe['time']} хв.")
            print(f"Інгредієнти: {', '.join(recipe['ingredients'])}")
            print(f"Інструкція: {recipe['instructions']}")
            print("-" * 30)
    except Exception as e:
        print(Fore.RED + "❌ Помилка відображення рецептів:" + Style.RESET_ALL, e)

def search_recipes():
    """Пошук рецепта за назвою."""
    try:
        name = input("Введіть назву рецепта для пошуку: ")
        recipe = collection.find_one({"name": {"$regex": name, "$options": "i"}})
        if recipe:
            print(f"Назва: {recipe['name']}, Категорія: {recipe['category']}, Час: {recipe['time']} хв.")
            print(f"Інгредієнти: {', '.join(recipe['ingredients'])}")
            print(f"Інструкція: {recipe['instructions']}")
        else:
            print(Fore.YELLOW + "❌ Рецепт не знайдено!" + Style.RESET_ALL)
    except Exception as e:
        print(Fore.RED + "❌ Помилка пошуку рецепта:" + Style.RESET_ALL, e)

def update_recipe():
    """Оновлення інформації про рецепт."""
    try:
        name = input("Введіть назву рецепта, який потрібно оновити: ")
        recipe = collection.find_one({"name": {"$regex": name, "$options": "i"}})
        if recipe:
            print(f"Знайдено рецепт: {recipe['name']}")
            new_time = input("Новий час приготування (хвилини): ")
            if not new_time.isdigit() or int(new_time) <= 0:
                print(Fore.RED + "❌ Введіть коректний час приготування!" + Style.RESET_ALL)
                return
            new_time = int(new_time)
            collection.update_one({"_id": recipe["_id"]}, {"$set": {"time": new_time}})
            print(Fore.GREEN + "✅ Рецепт оновлено!" + Style.RESET_ALL)
        else:
            print(Fore.YELLOW + "❌ Рецепт не знайдено!" + Style.RESET_ALL)
    except Exception as e:
        print(Fore.RED + "❌ Помилка оновлення рецепта:" + Style.RESET_ALL, e)

def delete_recipe():
    """Видалення рецепта."""
    try:
        name = input("Введіть назву рецепта, який потрібно видалити: ")
        result = collection.delete_one({"name": {"$regex": name, "$options": "i"}})
        if result.deleted_count > 0:
            print(Fore.GREEN + "✅ Рецепт видалено!" + Style.RESET_ALL)
        else:
            print(Fore.YELLOW + "❌ Рецепт не знайдено!" + Style.RESET_ALL)
    except Exception as e:
        print(Fore.RED + "❌ Помилка видалення рецепта:" + Style.RESET_ALL, e)

def export_recipes():
    """Експортує всі рецепти у JSON-файл."""
    try:
        recipes = list(collection.find())
        for recipe in recipes:
            recipe["_id"] = str(recipe["_id"])  # Конвертуємо ObjectId у строку
            if "created_at" in recipe:
                recipe["created_at"] = recipe["created_at"].strftime("%Y-%m-%d %H:%M:%S")  # Конвертуємо datetime у строку
        with open("recipes_backup.json", "w", encoding="utf-8") as file:
            json.dump(recipes, file, ensure_ascii=False, indent=4)
        print(Fore.GREEN + "✅ Рецепти успішно експортовано у recipes_backup.json!" + Style.RESET_ALL)
    except Exception as e:
        print(Fore.RED + "❌ Помилка експорту рецептів:" + Style.RESET_ALL, e)

# Головне меню
def main_menu():
    while True:
        print("\n" + Fore.CYAN + "=== Меню ===" + Style.RESET_ALL)
        print("1. Додати рецепт")
        print("2. Переглянути всі рецепти")
        print("3. Знайти рецепт")
        print("4. Оновити рецепт")
        print("5. Видалити рецепт")
        print("6. Експортувати рецепти у JSON")
        print("7. Вийти")
        
        choice = input("Оберіть дію: ")
        if choice == "1":
            add_recipe()
        elif choice == "2":
            view_recipes()
        elif choice == "3":
            search_recipes()
        elif choice == "4":
            update_recipe()
        elif choice == "5":
            delete_recipe()
        elif choice == "6":
            export_recipes()
        elif choice == "7":
            print(Fore.CYAN + "👋 До побачення!" + Style.RESET_ALL)
            break
        else:
            print(Fore.RED + "❌ Невірний вибір, спробуйте ще раз." + Style.RESET_ALL)

# Запуск програми
if __name__ == "__main__":
    main_menu()
