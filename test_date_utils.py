from datetime import date
import unittest

from ui.date_utils import (
    LAST_TRANSACTION_DATE_DAY_KEY,
    TRANSACTION_DATE_KEY,
    sync_transaction_date,
    transaction_date_needs_rollover,
)


class TransactionDateRolloverTests(unittest.TestCase):
    def test_initializes_transaction_date(self):
        session_state = {}
        today = date(2026, 11, 23)

        self.assertTrue(sync_transaction_date(session_state, today))
        self.assertEqual(session_state[TRANSACTION_DATE_KEY], today)
        self.assertEqual(session_state[LAST_TRANSACTION_DATE_DAY_KEY], today)

    def test_preserves_manual_date_until_next_day(self):
        today = date(2026, 11, 23)
        session_state = {
            LAST_TRANSACTION_DATE_DAY_KEY: today,
            TRANSACTION_DATE_KEY: date(2026, 11, 20),
        }

        self.assertFalse(sync_transaction_date(session_state, today))
        self.assertEqual(session_state[TRANSACTION_DATE_KEY], date(2026, 11, 20))

    def test_updates_date_after_midnight(self):
        yesterday = date(2026, 11, 23)
        today = date(2026, 11, 24)
        session_state = {
            LAST_TRANSACTION_DATE_DAY_KEY: yesterday,
            TRANSACTION_DATE_KEY: yesterday,
        }

        self.assertTrue(transaction_date_needs_rollover(session_state, today))
        self.assertTrue(sync_transaction_date(session_state, today))
        self.assertEqual(session_state[TRANSACTION_DATE_KEY], today)


if __name__ == "__main__":
    unittest.main()
