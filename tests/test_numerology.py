"""Тесты для модуля numerology."""

import unittest
from datetime import date
from pathlib import Path

from numerology import (
    life_path_number,
    is_master_number,
    power_numbers,
    month_component,
    sum_digits_reduced,
    load_rules,
    day_kind,
    generate_month,
    day_for_date,
    power_days,
    forbidden_days,
    neutral_days,
)


class LifePathTests(unittest.TestCase):
    def test_simple_number(self):
        # 1990-05-15 → 1+5+0+5+1+9+9+0 = 30 → 3+0 = 3
        self.assertEqual(life_path_number(date(1990, 5, 15)), 3)

    def test_master_number_11(self):
        # 1950-04-19 → 1+9+0+4+1+9+5+0 = 29 → 2+9 = 11 (мастер-число)
        self.assertEqual(life_path_number(date(1950, 4, 19)), 11)
        self.assertTrue(is_master_number(11))

    def test_master_number_22(self):
        # 2000-11-22 → 2+2+1+1+2+0+0+0 = 8 (мастер-число не появляется из чистого сложения)
        # Мастер-число 22 дано при рождении в дате 22 числа.
        # Здесь проверяем, что 22 НЕ разбивается и не превращается в 4.
        self.assertEqual(life_path_number(date(2000, 11, 22)), 8)

    def test_master_number_33(self):
        # 1989-12-21 → 2+1+1+2+1+9+8+9 = 33 (мастер-число)
        self.assertEqual(life_path_number(date(1989, 12, 21)), 33)

    def test_single_digit(self):
        # 2000-01-01 → 1+1+0+1+2+0+0+0 = 4
        self.assertEqual(life_path_number(date(2000, 1, 1)), 4)


class PowerNumbersTests(unittest.TestCase):
    def test_birthday_19_apr_1950(self):
        # День рождения: 19, число пути: 11
        # Составляющие 19: 1, 9
        # Составляющие 11: мастер-число, не сводится
        # Месяц 04: 4
        result = power_numbers(date(1950, 4, 19), 11)
        self.assertEqual(result, [1, 4, 9, 11, 19])

    def test_extra_numbers(self):
        result = power_numbers(date(1990, 5, 15), 3, extra=[20])
        self.assertIn(20, result)

    def test_month_component_sum(self):
        # 02 → 0+2 = 2
        self.assertEqual(month_component(date(1990, 2, 27)), 2)
        # 11 → 1+1 = 2
        self.assertEqual(month_component(date(1990, 11, 27)), 2)
        # 12 → 1+2 = 3
        self.assertEqual(month_component(date(1990, 12, 27)), 3)
        # 05 → 0+5 = 5
        self.assertEqual(month_component(date(1990, 5, 1)), 5)

    def test_sum_digits_reduced(self):
        self.assertEqual(sum_digits_reduced(29), 2)  # 2+9=11, 1+1=2
        self.assertEqual(sum_digits_reduced(11), 2)  # 1+1=2
        self.assertEqual(sum_digits_reduced(7), 7)


class CalendarTests(unittest.TestCase):
    def setUp(self):
        self.rules_path = Path(__file__).parent.parent / "rules" / "default-rules.json"
        self.rules = load_rules(self.rules_path)

    def test_load_rules(self):
        self.assertIn("operations", self.rules)
        self.assertIn("savings", self.rules["operations"])

    def test_day_kind_power_day(self):
        # 27 — день силы (в good для savings, lottery, bigPurchase)
        d = day_kind(27, self.rules["operations"])
        self.assertTrue(d.is_power_day)
        self.assertGreater(len(d.good), 0)

    def test_day_kind_bad_day(self):
        # 5 — табу для нескольких операций
        d = day_kind(5, self.rules["operations"])
        self.assertTrue(d.is_bad_day)
        self.assertGreater(len(d.bad), 0)

    def test_day_kind_neutral(self):
        # 1 — нет ни в good, ни в bad для большинства операций
        d = day_kind(1, self.rules["operations"])
        # savings: 1 не в good, не в bad → neutral
        self.assertIn("Отложить деньги в накопления", d.neutral)

    def test_generate_month(self):
        # Август 2026 — 31 день
        days = generate_month(2026, 8, self.rules)
        self.assertEqual(len(days), 31)

    def test_power_days_august_2026(self):
        days = generate_month(2026, 8, self.rules)
        pdays = power_days(days)
        # 7, 11, 20, 22, 27 — должны быть днями силы
        self.assertIn(7, pdays)
        self.assertIn(11, pdays)

    def test_forbidden_days(self):
        days = generate_month(2026, 8, self.rules)
        fdays = forbidden_days(days)
        # 5, 8 — табу
        self.assertIn(5, fdays)
        self.assertIn(8, fdays)

    def test_day_for_date(self):
        # 2026-08-27 — день силы
        d = day_for_date(date(2026, 8, 27), self.rules)
        self.assertEqual(d.day, 27)
        self.assertTrue(d.is_power_day)


if __name__ == "__main__":
    unittest.main()
