"""Расчёт числа жизненного пути по дате рождения.

Используется классическая система нумерологии Пифагора:
- Складываются все цифры даты рождения (день, месяц, год).
- Если получается двузначное число (и это не мастер-число 11, 22, 33) —
  цифры складываются ещё раз.
- Мастер-числа 11, 22, 33 сохраняются без дальнейшего редуцирования.

Источник: классическая нумерология Пифагора (общедоступная).
"""

from datetime import date

MASTER_NUMBERS = {11, 22, 33}


def sum_digits(n: int) -> int:
    """Сумма цифр числа."""
    return sum(int(d) for d in str(abs(n)))


def life_path_number(birth_date: date) -> int:
    """Вычисляет число жизненного пути.

    Примеры:
        1990-05-15 → 1+5+0+5+1+9+9+0 = 30 → 3+0 = 3
        1950-04-19 → 1+9+0+4+1+9+5+0 = 29 → 2+9 = 11 (мастер-число)
        2000-11-22 → 2+2+1+1+2+0+0+0 = 8  (22 — мастер-число, не сводится)
    """
    digits = f"{birth_date.day:02d}{birth_date.month:02d}{birth_date.year:04d}"
    total = sum(int(d) for d in digits)

    while total > 9 and total not in MASTER_NUMBERS:
        total = sum_digits(total)

    return total


def is_master_number(n: int) -> bool:
    """Является ли число мастер-числом (11, 22, 33)."""
    return n in MASTER_NUMBERS
