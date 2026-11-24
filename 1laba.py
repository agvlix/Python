import argparse
import sys
import FreeSimpleGUI as sg
from cli import run_cli
from deck import SPHERES
from storage import (
    build_stats_text,
    create_spread_record,
    delete_record_by_id,
    draw_daily_record,
    format_listbox_items,
    format_record_details,
    load_data,
    search_records_data,
)


def run_gui() -> None:
    sg.theme("DarkTeal12")

    displayed_records: list[dict] = load_data()

    layout = [
        [sg.Text("Керування розкладами та записами", font=("Segoe UI", 15, "bold"))],
        [sg.HorizontalSeparator()],
        [
            sg.Text("Сфера:", size=(10, 1)),
            sg.Combo(SPHERES, default_value=SPHERES[0], readonly=True, key="-SPHERE-", size=(22, 1)),
            sg.Text("Питання:", size=(8, 1)),
            sg.Input(key="-QUESTION-", expand_x=True),
        ],
        [
            sg.Push(),
            sg.Button("Новий розклад", key="-CREATE-", button_color=("white", "#2b6cb0")),
            sg.Button("Карта дня", key="-DAILY-", button_color=("white", "#2f855a")),
        ],
        [
            sg.Text("Пошук:", size=(10, 1)),
            sg.Input(key="-SEARCH-", expand_x=True),
            sg.Button("Знайти", key="-FIND-"),
            sg.Button("Усі записи", key="-ALL-"),
        ],
        [
            sg.Listbox(
                values=format_listbox_items(displayed_records),
                key="-LIST-",
                size=(85, 12),
                expand_x=True,
                expand_y=True,
                enable_events=True,
                select_mode=sg.LISTBOX_SELECT_MODE_SINGLE,
            )
        ],
        [
            sg.Button("Деталі вибраного", key="-DETAILS-"),
            sg.Button("Видалити вибране", key="-DELETE-", button_color=("white", "#c53030")),
            sg.Button("Статистика", key="-STATS-"),
            sg.Push(),
            sg.Button("Вихід", key="-EXIT-"),
        ],
        [sg.Text("Готово до роботи.", key="-STATUS-", text_color="#a0aec0", expand_x=True)],
    ]

    window = sg.Window("TaskHub / Tarot Manager GUI", layout, resizable=True, finalize=True)

    def refresh_list(records: list[dict], status_msg: str | None = None) -> None:
        nonlocal displayed_records
        displayed_records = records
        window["-LIST-"].update(format_listbox_items(displayed_records))
        if status_msg:
            window["-STATUS-"].update(status_msg)

    def get_selected_record(values: dict) -> dict | None:
        selected_indices = values.get("-LIST-", [])
        if not selected_indices:
            return None
        idx = selected_indices[0]
        if 0 <= idx < len(displayed_records):
            return displayed_records[idx]
        return None

    while True:
        event, values = window.read()
        if event in (sg.WINDOW_CLOSED, "-EXIT-"):
            break

        if event == "-CREATE-":
            sphere = values.get("-SPHERE-", "Загальне")
            ok, msg, rec = create_spread_record(values["-QUESTION-"], sphere=sphere)
            if not ok or rec is None:
                sg.popup_error(msg, title="Помилка введення")
                window["-STATUS-"].update(f"Помилка: {msg}")
            else:
                window["-QUESTION-"].update("")
                refresh_list(load_data(), f"Додано запис #{rec['id']} [{rec['sphere']}]: {rec['card']}.")
                sg.popup(
                    format_record_details(rec),
                    title="Новий розклад",
                )

        elif event == "-DAILY-":
            sphere = values.get("-SPHERE-", "Загальне")
            rec = draw_daily_record(sphere=sphere)
            refresh_list(load_data(), f"Карта дня [{rec['sphere']}]: {rec['card']}.")
            sg.popup(
                format_record_details(rec),
                title="Карта дня",
            )

        elif event == "-FIND-":
            ok, err, found = search_records_data(values["-SEARCH-"])
            if not ok:
                sg.popup_error(err, title="Помилка пошуку")
                window["-STATUS-"].update(f"Помилка: {err}")
            elif not found:
                refresh_list([], f"За запитом '{values['-SEARCH-'].strip()}' нічого не знайдено.")
                sg.popup_ok("За вашим запитом записів не знайдено.", title="Пошук")
            else:
                refresh_list(found, f"Знайдено записів: {len(found)}.")

        elif event == "-ALL-":
            window["-SEARCH-"].update("")
            all_recs = load_data()
            refresh_list(all_recs, f"Показано всі записи ({len(all_recs)}).")

        elif event in ("-DETAILS-", "-LIST-"):
            rec = get_selected_record(values)
            if rec is None:
                if event == "-DETAILS-":
                    sg.popup_warning("Спочатку оберіть запис у списку!", title="Запис не вибрано")
                    window["-STATUS-"].update("Помилка: запис у списку не вибрано.")
                continue

            if event == "-DETAILS-":
                sg.popup(
                    format_record_details(rec),
                    title=f"Запис #{rec['id']}",
                )
            else:
                window["-STATUS-"].update(
                    f"Вибрано #{rec['id']} [{rec.get('sphere', 'Загальне')}]: {rec['card']} — {rec['question']}"
                )

        elif event == "-DELETE-":
            rec = get_selected_record(values)
            if rec is None:
                sg.popup_warning("Оберіть запис, який потрібно видалити!", title="Запис не вибрано")
                window["-STATUS-"].update("Помилка: не вибрано запис для видалення.")
                continue

            confirm = sg.popup_yes_no(
                f"Видалити запис #{rec['id']} ({rec['card']})?",
                title="Підтвердження видалення",
            )
            if confirm == "Yes":
                if delete_record_by_id(rec["id"]):
                    refresh_list(load_data(), f"Запис #{rec['id']} видалено.")
                else:
                    sg.popup_error("Не вдалося видалити запис.", title="Помилка")

        elif event == "-STATS-":
            stats_text = build_stats_text(load_data())
            window["-STATUS-"].update("Оновлено статистику.")
            sg.popup_scrolled(stats_text, title="Статистика випадінь", size=(55, 18))

    window.close()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="GUI та CLI застосунок для керування записами (tarot.json)")
    parser.add_argument("--cli", action="store_true", help="Запустити в консольному режимі")

    subparsers = parser.add_subparsers(dest="command")

    p_add = subparsers.add_parser("add", help="Створити новий розклад")
    p_add.add_argument("question", nargs="?", default="", help="Питання для розкладу")
    p_add.add_argument("--sphere", default="Загальне", choices=SPHERES, help="Сфера життя")

    p_daily = subparsers.add_parser("daily", help="Витягнути карту дня")
    p_daily.add_argument("--sphere", default="Загальне", choices=SPHERES, help="Сфера життя")

    subparsers.add_argument("--list_placeholder", action="store_true") if False else None
    subparsers.add_parser("list", help="Показати всі записи")

    p_search = subparsers.add_parser("search", help="Пошук за запитом, сферою або картою")
    p_search.add_argument("query", nargs="?", default="", help="Ключове слово")

    p_del = subparsers.add_parser("delete", help="Видалити запис за ID")
    p_del.add_argument("--id", type=int, help="ID запису")

    subparsers.add_parser("stats", help="Показати статистику")

    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.cli or args.command is not None:
        sys.exit(run_cli(args))
    run_gui()


if __name__ == "__main__":
    main()