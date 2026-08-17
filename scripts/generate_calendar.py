"""CLI: сгенерировать финансовый календарь на месяц по дате рождения.

Использование:
    python scripts/generate_calendar.py --birthdate 1990-05-15 --month 2026-08
    python scripts/generate_calendar.py --birthdate 1990-05-15 --today

Пример вывода:
    === Финансовый календарь на август 2026 ===
    Дата рождения: 1990-05-15
    Число жизненного пути: 3
    Числа силы: [1, 3, 5, 15]

    Дни силы: 1, 3, 5, 7, 11, 15, 20, 22, 27, 33
    Дни-табу: 8, 13, 14, 17, 23, 26, 29
    Нейтральные: 2, 4, 6, 9, 10, 12, 16, 18, 19, 21, 24, 25, 28, 30, 31

    По каждому дню силы:
      7 (пятница): ✅ Можно — Отложить деньги в накопления, Оплата подписок, Купить лотерейный билет, Крупная покупка
      11 (вторник): ✅ Можно — Отложить деньги в накопления, Купить лотерейный билет, Крупная покупка
      ...
"""

import argparse
import sys
from datetime import date, datetime
from pathlib import Path

PROJECT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_DIR))

# Корректный вывод кириллицы и эмодзи в Windows-консоли (cp1251)
try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass

from numerology import life_path_number, power_numbers, load_rules, generate_month, day_for_date, power_days, forbidden_days, neutral_days  # noqa: E402

WEEKDAY_NAMES = {
    0: "понедельник", 1: "вторник", 2: "среда", 3: "четверг",
    4: "пятница", 5: "суббота", 6: "воскресенье",
}


def calc_payroll_dates(year: int, month: int, rules: dict) -> list[tuple[str, date]]:
    """Возвращает [(label, date)] для каждой выплаты, попавшей в месяц."""
    from datetime import timedelta

    payroll = rules.get("payroll", {})
    result = []
    for key, cfg in payroll.items():
        # Пропускаем служебные ключи (например, _comment)
        if not isinstance(cfg, dict):
            continue
        day = cfg.get("day")
        label = cfg.get("label", key)
        if not day:
            continue
        try:
            d = date(year, month, day)
        except ValueError:
            continue
        # Перенос с выходных на предыдущий рабочий день
        while d.weekday() >= 5:
            d -= timedelta(days=1)
        result.append((label, d))
    return result


def print_month_calendar(year: int, month: int, birth_date: date, rules: dict) -> None:
    lp = life_path_number(birth_date)
    pn = power_numbers(birth_date, lp)
    days = generate_month(year, month, rules)
    operations = rules.get("operations", {})

    month_name = [
        "январь", "февраль", "март", "апрель", "май", "июнь",
        "июль", "август", "сентябрь", "октябрь", "ноябрь", "декабрь",
    ][month - 1]

    print(f"=== Финансовый календарь на {month_name} {year} ===")
    print(f"Дата рождения: {birth_date.isoformat()}")
    print(f"Число жизненного пути: {lp}")
    print(f"Числа силы: {pn}")
    print()

    pdays = power_days(days)
    fdays = forbidden_days(days)
    ndays = neutral_days(days)

    print(f"Дни силы: {pdays}")
    print(f"Дни-табу: {fdays}")
    print(f"Нейтральные: {ndays}")
    print()

    payroll_dates = calc_payroll_dates(year, month, rules)
    if payroll_dates:
        print("Выплаты:")
        for label, d in payroll_dates:
            print(f"  {d.isoformat()} ({WEEKDAY_NAMES[d.weekday()]}) — {label}")
        print()

    print("Дни силы (детально):")
    for d in days:
        if not d.is_power_day:
            continue
        try:
            full_date = date(year, month, d.day)
        except ValueError:
            continue
        wd = WEEKDAY_NAMES[full_date.weekday()]
        print(f"  {d.day:>2} ({wd}):")
        for label in d.good:
            print(f"    ✅ {label}")
        if d.bad:
            for label in d.bad:
                print(f"    ❌ {label}")
        if d.neutral:
            print(f"    ⚪ Нейтральные: {', '.join(d.neutral)}")
        print()


def print_today(birth_date: date, rules: dict) -> None:
    today = date.today()
    lp = life_path_number(birth_date)
    pn = power_numbers(birth_date, lp)
    fd = day_for_date(today, rules)

    print(f"=== {today.isoformat()} ({WEEKDAY_NAMES[today.weekday()]}) ===")
    print(f"Дата рождения: {birth_date.isoformat()}")
    print(f"Число жизненного пути: {lp}")
    print(f"Числа силы: {pn}")
    print()

    if fd.is_power_day:
        print("✅ ДЕНЬ СИЛЫ")
    elif fd.is_bad_day:
        print("❌ ДЕНЬ-ТАБУ")
    else:
        print("⚪ Нейтральный день")

    if fd.good:
        print("\nМожно:")
        for label in fd.good:
            print(f"  - {label}")
    if fd.bad:
        print("\nНельзя:")
        for label in fd.bad:
            print(f"  - {label}")
    if fd.neutral:
        print("\nНейтральные (можно, но без силы):")
        for label in fd.neutral:
            print(f"  - {label}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Финансовый календарь по нумерологии")
    parser.add_argument("--birthdate", required=True, help="Дата рождения в формате YYYY-MM-DD")
    parser.add_argument("--month", help="Месяц в формате YYYY-MM (по умолчанию — текущий)")
    parser.add_argument("--today", action="store_true", help="Показать статус на сегодня")
    parser.add_argument("--rules", default=str(PROJECT_DIR / "rules" / "default-rules.json"),
                        help="Путь к файлу правил")

    args = parser.parse_args()
    birth_date = datetime.strptime(args.birthdate, "%Y-%m-%d").date()
    rules = load_rules(args.rules)

    if args.today:
        print_today(birth_date, rules)
    else:
        if args.month:
            year, month = map(int, args.month.split("-"))
        else:
            today = date.today()
            year, month = today.year, today.month
        print_month_calendar(year, month, birth_date, rules)

    return 0


if __name__ == "__main__":
    sys.exit(main())
