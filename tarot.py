import json
import random

DATA_FILE = "tarot.json"

TAROT_DECK = [
    {"id": 0, "name": "Шут", "meaning": "Нові починання, свобода та ризик."},
    {"id": 1, "name": "Маг", "meaning": "Концентрація сил, майстерність та ідеї."},
    {"id": 2, "name": "Верховна Жриця", "meaning": "Інтуїція, таємниці та довіра до себе."},
    {"id": 3, "name": "Імператриця", "meaning": "Достаток, творчість і турбота."},
    {"id": 4, "name": "Імператор", "meaning": "Порядок, дисципліна та контроль."},
    {"id": 5, "name": "Ієрофант", "meaning": "Навчання, традиції та поради."},
    {"id": 6, "name": "Закохані", "meaning": "Вибір, стосунки та важливі рішення."},
    {"id": 7, "name": "Колісниця", "meaning": "Прорив, рух уперед і цілеспрямованість."},
    {"id": 8, "name": "Справедливість", "meaning": "Баланс, чесність і зважені рішення."},
    {"id": 9, "name": "Відлюдник", "meaning": "Аналіз, роздуми та внутрішній пошук."},
    {"id": 10, "name": "Колесо Фортуни", "meaning": "Зміни, доля та новий цикл."},
    {"id": 11, "name": "Сила", "meaning": "Внутрішня стійкість і мужність."},
    {"id": 12, "name": "Повішений", "meaning": "Пауза та погляд під іншим кутом."},
    {"id": 13, "name": "Смерть", "meaning": "Трансформація та завершення етапу."},
    {"id": 14, "name": "Помірність", "meaning": "Баланс, спокій і компроміс."},
    {"id": 15, "name": "Диявол", "meaning": "Спокуси, ілюзії та приховані бажання."},
    {"id": 16, "name": "Вежа", "meaning": "Різкі зміни та руйнування ілюзій."},
    {"id": 17, "name": "Зірка", "meaning": "Надія, натхнення та віра в майбутнє."},
    {"id": 18, "name": "Місяць", "meaning": "Ілюзії, страхи та невизначеність."},
    {"id": 19, "name": "Сонце", "meaning": "Успіх, радість і ясність."},
    {"id": 20, "name": "Суд", "meaning": "Пробудження та остаточні висновки."},
    {"id": 21, "name": "Світ", "meaning": "Завершення циклу та гармонія."}
]


def load_data():
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return []


def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def create_spread():
    question = input("Введіть своє питання: ").strip()

    if not question:
        print("\n[!] Помилка: Питання не може бути порожнім!\n")
        return

    records = load_data()
    card = random.choice(TAROT_DECK)

    new_record = {
        "id": len(records) + 1,
        "type": "Індивідуальний розклад",
        "question": question,
        "card": card["name"],
        "meaning": card["meaning"]
    }

    records.append(new_record)
    save_data(records)

    print(f"\n Розклад ")
    print(f"Питання: {question}")
    print(f"Карта: {card['name']} — {card['meaning']}\n")


def draw_daily():
    records = load_data()
    card = random.choice(TAROT_DECK)

    new_record = {
        "id": len(records) + 1,
        "type": "Карта дня",
        "question": "Яка енергія дня очікує?",
        "card": card["name"],
        "meaning": card["meaning"]
    }

    records.append(new_record)
    save_data(records)

    print(f"\nКарта дня ")
    print(f"Аркан: {card['name']} — {card['meaning']}\n")


def show_records():
    records = load_data()

    if not records:
        print("\n[!] Архів поки що порожній.\n")
        return

    print("\nАРХІВ РОЗКЛАДІВ")
    for r in records:
        print(f"#{r['id']} [{r['type']}] Питання: {r['question']}")
        print(f"   -> Карта: {r['card']} ({r['meaning']})")
        print("-" * 35 + "\n")


def search_records():
    query = input("Введіть ключове слово для пошуку: ").strip().lower()

    if not query:
        print("\n[!] Помилка: Пошуковий запит не може бути порожнім!\n")
        return

    records = load_data()
    found = [r for r in records if query in r['question'].lower() or query in r['card'].lower()]

    if not found:
        print(f"\n[!] За запитом '{query}' нічого не знайдено.\n")
        return

    print(f"\nРЕЗУЛЬТАТИ ПОШУКУ ('{query}')")
    for r in found:
        print(f"#{r['id']} Питання: {r['question']} | Карта: {r['card']} ({r['meaning']})")
        print("-" * 35 + "\n")


def show_stats():
    records = load_data()

    if not records:
        print("\n[!] Статистика недоступна: архів порожній.\n")
        return

    card_counts = {}
    for r in records:
        c_name = r["card"]
        card_counts[c_name] = card_counts.get(c_name, 0) + 1

    most_frequent = max(card_counts, key=card_counts.get)

    print("\nСТАТИСТИКА")
    print(f"Всього збережено записів: {len(records)}")
    print(f"Найчастіша карта: {most_frequent} (зустрічається {card_counts[most_frequent]} раз(и))")
    print("-" * 25 + "\n")


def main():
    while True:
        print("Меню команд:")
        print("  add    - Створити новий розклад")
        print("  daily  - Карта дня")
        print("  show   - Показати всі записи")
        print("  search - Пошук за запитом або картою")
        print("  stats  - Статистика випадінь")
        print("  exit   - Вийти з програми")

        choice = input("\nВведіть команду: ").strip().lower()

        if choice == "add":
            create_spread()
        elif choice == "daily":
            draw_daily()
        elif choice == "show":
            show_records()
        elif choice == "search":
            search_records()
        elif choice == "stats":
            show_stats()
        elif choice == "exit" or choice == "quit":
            print("Вихід з програми...")
            break
        else:
            print("\n[!] Помилка: Невідома команда. Використовуйте: add, daily, show, search, stats, exit.\n")


if __name__ == "__main__":
    main()