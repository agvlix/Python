import json
import os
import random
import sys
from deck import SPHERES, TAROT_DECK, get_sphere_meaning

DATA_FILE = "tarot.json"


def get_data_path() -> str:
    if getattr(sys, "frozen", False):
        base_dir = os.path.dirname(sys.executable)
    else:
        base_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_dir, DATA_FILE)


def load_data() -> list[dict]:
    path = get_data_path()
    if not os.path.exists(path):
        return []
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data if isinstance(data, list) else []
    except (json.JSONDecodeError, OSError):
        return []


def save_data(data: list[dict]) -> None:
    path = get_data_path()
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def next_record_id(records: list[dict]) -> int:
    if not records:
        return 1
    return max(r.get("id", 0) for r in records) + 1


def create_spread_record(question: str, sphere: str = "Загальне") -> tuple[bool, str, dict | None]:
    cleaned = question.strip()
    if not cleaned:
        return False, "Питання не може бути порожнім!", None

    chosen_sphere = sphere if sphere in SPHERES else "Загальне"
    records = load_data()
    card = random.choice(TAROT_DECK)
    sphere_text = get_sphere_meaning(card["name"], chosen_sphere, card["meaning"])

    record = {
        "id": next_record_id(records),
        "type": "Індивідуальний розклад",
        "sphere": chosen_sphere,
        "question": cleaned,
        "card": card["name"],
        "meaning": card["meaning"],
        "sphere_meaning": sphere_text,
    }
    records.append(record)
    save_data(records)
    return True, f"Випала карта: {card['name']} — {sphere_text}", record


def draw_daily_record(sphere: str = "Загальне") -> dict:
    chosen_sphere = sphere if sphere in SPHERES else "Загальне"
    records = load_data()
    card = random.choice(TAROT_DECK)
    sphere_text = get_sphere_meaning(card["name"], chosen_sphere, card["meaning"])

    record = {
        "id": next_record_id(records),
        "type": "Карта дня",
        "sphere": chosen_sphere,
        "question": "Яка енергія дня очікує?",
        "card": card["name"],
        "meaning": card["meaning"],
        "sphere_meaning": sphere_text,
    }
    records.append(record)
    save_data(records)
    return record


def search_records_data(query: str) -> tuple[bool, str, list[dict]]:
    cleaned = query.strip().lower()
    if not cleaned:
        return False, "Пошуковий запит не може бути порожнім!", []

    records = load_data()
    found = [
        r
        for r in records
        if cleaned in r.get("question", "").lower()
        or cleaned in r.get("card", "").lower()
        or cleaned in r.get("type", "").lower()
        or cleaned in r.get("sphere", "").lower()
    ]
    return True, "", found


def delete_record_by_id(record_id: int) -> bool:
    records = load_data()
    updated = [r for r in records if r.get("id") != record_id]
    if len(updated) == len(records):
        return False
    save_data(updated)
    return True


def delete_record(record: dict, fallback_index: int | None = None) -> bool:
    records = load_data()
    rec_id = record.get("id")

    if rec_id is not None:
        updated = [r for r in records if r.get("id") != rec_id]
        if len(updated) != len(records):
            save_data(updated)
            return True

    if fallback_index is not None and 0 <= fallback_index < len(records):
        if records[fallback_index] == record:
            records.pop(fallback_index)
            save_data(records)
            return True

    return False


def build_stats_text(records: list[dict]) -> str:
    if not records:
        return "Статистика недоступна: архів порожній."

    card_counts: dict[str, int] = {}
    sphere_counts: dict[str, int] = {}
    for r in records:
        c_name = r.get("card", "Невідома")
        s_name = r.get("sphere", "Загальне")
        card_counts[c_name] = card_counts.get(c_name, 0) + 1
        sphere_counts[s_name] = sphere_counts.get(s_name, 0) + 1

    most_frequent = max(card_counts, key=card_counts.get)
    max_count = card_counts[most_frequent]

    lines = [
        f"Всього збережено записів: {len(records)}",
        f"Найчастіша карта: {most_frequent} (зустрічається {max_count} раз(и))",
        "",
        "За сферами:",
    ]
    for s_name, s_cnt in sorted(sphere_counts.items(), key=lambda x: (-x[1], x[0])):
        lines.append(f"  • {s_name}: {s_cnt}")

    lines.append("")
    lines.append("Розподіл за картами:")
    for name, count in sorted(card_counts.items(), key=lambda x: (-x[1], x[0])):
        lines.append(f"  • {name}: {count}")
    return "\n".join(lines)


def format_record_details(rec: dict) -> str:
    sphere = rec.get("sphere", "Загальне")
    sphere_meaning = rec.get("sphere_meaning") or get_sphere_meaning(
        rec.get("card", ""), sphere, rec.get("meaning", "")
    )
    general_meaning = rec.get("meaning", "")

    return (
        f"ID: #{rec['id']}\n"
        f"Тип: {rec['type']}\n"
        f"Сфера: {sphere}\n"
        f"Питання: {rec['question']}\n"
        f"Карта: {rec['card']}\n\n"
        f"Трактовка для сфери ({sphere}):\n{sphere_meaning}\n\n"
        f"Загальне значення аркану:\n{general_meaning}"
    )


def format_listbox_items(records: list[dict]) -> list[str]:
    return [
        f"#{r['id']} | [{r.get('sphere', 'Загальне')}] {r['card']} — {r['question']}"
        for r in records
    ]