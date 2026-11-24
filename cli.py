import argparse
from deck import SPHERES
from storage import (
    build_stats_text,
    create_spread_record,
    delete_record_by_id,
    draw_daily_record,
    load_data,
    search_records_data,
)


def _choose_sphere_interactive() -> str:
    print("Оберіть сферу:")
    for idx, s in enumerate(SPHERES, start=1):
        print(f"  {idx}. {s}")
    raw = input(f"Номер сфери [1-{len(SPHERES)}, Enter = Загальне]: ").strip()
    if raw.isdigit():
        num = int(raw)
        if 1 <= num <= len(SPHERES):
            return SPHERES[num - 1]
    return "Загальне"


def run_cli(args: argparse.Namespace) -> int:
    cmd = args.command
    sphere = getattr(args, "sphere", "Загальне") or "Загальне"

    if cmd == "add":
        ok, msg, rec = create_spread_record(args.question or "", sphere=sphere)
        if not ok or rec is None:
            print(f"[!] Помилка: {msg}")
            return 1
        print("\nНовий розклад створено:")
        print(f"  #{rec['id']} [{rec['sphere']}] Питання: {rec['question']}")
        print(f"  Карта: {rec['card']}")
        print(f"  Трактовка ({rec['sphere']}): {rec['sphere_meaning']}")
        print(f"  Загальне: {rec['meaning']}\n")
        return 0

    if cmd == "daily":
        rec = draw_daily_record(sphere=sphere)
        print("\nКарта дня:")
        print(f"  #{rec['id']} [{rec['sphere']}] Аркан: {rec['card']}")
        print(f"  Трактовка ({rec['sphere']}): {rec['sphere_meaning']}")
        print(f"  Загальне: {rec['meaning']}\n")
        return 0

    if cmd == "list":
        records = load_data()
        if not records:
            print("\n[!] Архів поки що порожній.\n")
            return 0
        print("\nАРХІВ ЗАПИСІВ")
        for r in records:
            sp = r.get("sphere", "Загальне")
            tr = r.get("sphere_meaning") or r.get("meaning", "")
            print(f"#{r['id']} [{r['type']} | {sp}] Питання: {r['question']}")
            print(f"   -> Карта: {r['card']} — {tr}")
        print("-" * 45 + "\n")
        return 0

    if cmd == "search":
        ok, err, found = search_records_data(args.query or "")
        if not ok:
            print(f"[!] Помилка: {err}")
            return 1
        if not found:
            print(f"\n[!] За запитом '{args.query}' нічого не знайдено.\n")
            return 0
        print(f"\nРЕЗУЛЬТАТИ ПОШУКУ ('{args.query}')")
        for r in found:
            sp = r.get("sphere", "Загальне")
            tr = r.get("sphere_meaning") or r.get("meaning", "")
            print(f"#{r['id']} [{sp}] Питання: {r['question']} | Карта: {r['card']} — {tr}")
        print("-" * 45 + "\n")
        return 0

    if cmd == "delete":
        if args.id is None:
            print("[!] Помилка: вкажіть --id запису для видалення.")
            return 1
        if delete_record_by_id(args.id):
            print(f"[OK] Запис #{args.id} видалено.")
            return 0
        print(f"[!] Запис з ID #{args.id} не знайдено.")
        return 1

    if cmd == "stats":
        print("\nСТАТИСТИКА")
        print(build_stats_text(load_data()))
        print()
        return 0

    while True:
        print("\nМеню (CLI):")
        print("  1. Створити новий розклад")
        print("  2. Карта дня")
        print("  3. Показати всі записи")
        print("  4. Пошук за запитом, сферою або картою")
        print("  5. Статистика випадінь")
        print("  6. Вийти")
        choice = input("\nОберіть дію (1-6): ").strip()

        if choice == "1":
            q = input("Введіть своє питання: ")
            sp = _choose_sphere_interactive()
            ok, msg, rec = create_spread_record(q, sphere=sp)
            if not ok or rec is None:
                print(f"\n[!] Помилка: {msg}\n")
            else:
                print(f"\nКарта: {rec['card']} [{rec['sphere']}]")
                print(f"Трактовка: {rec['sphere_meaning']}\n")
        elif choice == "2":
            sp = _choose_sphere_interactive()
            rec = draw_daily_record(sphere=sp)
            print(f"\nКарта дня: {rec['card']} [{rec['sphere']}]")
            print(f"Трактовка: {rec['sphere_meaning']}\n")
        elif choice == "3":
            records = load_data()
            if not records:
                print("\n[!] Архів порожній.\n")
            else:
                for r in records:
                    print(f"#{r['id']} [{r.get('sphere', 'Загальне')}] {r['question']} -> {r['card']}")
        elif choice == "4":
            q = input("Ключове слово: ")
            ok, err, found = search_records_data(q)
            if not ok:
                print(f"\n[!] Помилка: {err}\n")
            elif not found:
                print("\n[!] Нічого не знайдено.\n")
            else:
                for r in found:
                    print(f"#{r['id']} [{r['card']}] {r['question']} — {r.get('sphere_meaning') or r['meaning']}")
        elif choice == "5":
            print("\n" + build_stats_text(load_data()) + "\n")
        elif choice == "6" or choice.lower() == "exit":
            break
        else:
            print("\n[!] Введіть число від 1 до 6.\n")
    return 0