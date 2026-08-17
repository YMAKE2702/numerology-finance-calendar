"""Генерация финансового календаря на месяц по числам силы.

Для каждого дня месяца определяется, какие финансовые операции
рекомендуется делать (good), какие не рекомендуется (bad),
а какие нейтральны (neutral).

Правила задаются в json-файле конфигурации (rules.json).
"""

import calendar
import json
from datetime import date
from pathlib import Path


class FinanceDay:
    """Один день финансового календаря."""

    def __init__(self, day: int, good: list[str], bad: list[str], neutral: list[str]):
        self.day = day
        self.good = good
        self.bad = bad
        self.neutral = neutral

    @property
    def is_power_day(self) -> bool:
        """Является ли день «днём силы» (есть хотя бы одна good-операция)."""
        return bool(self.good)

    @property
    def is_bad_day(self) -> bool:
        """Является ли день «табу» (есть хотя бы одна bad-операция)."""
        return bool(self.bad)

    def to_dict(self) -> dict:
        return {
            "day": self.day,
            "good": self.good,
            "bad": self.bad,
            "neutral": self.neutral,
        }


def load_rules(path: str | Path) -> dict:
    """Загружает правила из json-файла.

    Структура rules.json:
        {
            "operations": {
                "savings": {
                    "label": "Отложить деньги с зарплаты в накопления",
                    "good": [7, 11, 27],
                    "bad": [5, 8, 14, 23, 26]
                },
                ...
            }
        }
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Файл правил не найден: {path}")
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    if "operations" not in data:
        raise ValueError("В файле правил должен быть ключ 'operations'")
    return data


def day_kind(day_of_month: int, operations: dict) -> FinanceDay:
    """Определяет статус дня по всем операциям.

    Если день входит в good хотя бы одной операции — это «день силы».
    Если только в bad — это «табу». Иначе — нейтральный.
    """
    good = []
    bad = []
    neutral = []

    for key, op in operations.items():
        label = op.get("label", key)
        good_days = op.get("good", [])
        bad_days = op.get("bad", [])

        if day_of_month in good_days:
            good.append(label)
        elif day_of_month in bad_days:
            bad.append(label)
        else:
            neutral.append(label)

    return FinanceDay(day_of_month, good, bad, neutral)


def generate_month(year: int, month: int, rules: dict) -> list[FinanceDay]:
    """Генерирует список FinanceDay для всего месяца.

    Args:
        year: год (например, 2026).
        month: месяц (1-12).
        rules: правила (результат load_rules).

    Returns:
        Список FinanceDay для каждого дня месяца.
    """
    days_in_month = calendar.monthrange(year, month)[1]
    operations = rules.get("operations", {})
    return [day_kind(d, operations) for d in range(1, days_in_month + 1)]


def power_days(month_days: list[FinanceDay]) -> list[int]:
    """Возвращает список «дней силы» (хороших дней) в месяце."""
    return [d.day for d in month_days if d.is_power_day]


def forbidden_days(month_days: list[FinanceDay]) -> list[int]:
    """Возвращает список «табу-дней» в месяце."""
    return [d.day for d in month_days if d.is_bad_day]


def neutral_days(month_days: list[FinanceDay]) -> list[int]:
    """Возвращает список нейтральных дней в месяце."""
    return [d.day for d in month_days if not d.is_power_day and not d.is_bad_day]


def day_for_date(target_date: date, rules: dict) -> FinanceDay:
    """Возвращает FinanceDay для конкретной даты."""
    return day_kind(target_date.day, rules.get("operations", {}))
