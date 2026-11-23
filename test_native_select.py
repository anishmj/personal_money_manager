from types import SimpleNamespace
import unittest
from unittest.mock import patch

import ui.native_select as native_select


class NativeSelectTests(unittest.TestCase):
    def test_selected_value_maps_to_original_option(self):
        state = {"category-picker": "Cafe"}
        with patch.object(
            native_select, "st", SimpleNamespace(session_state=state)
        ), patch.object(
            native_select, "_COMPONENT", return_value="Cafe"
        ) as component:
            selected = native_select.native_selectbox(
                "Category",
                ["Choose category", "Food", "Cafe"],
                key="category-picker"
            )

        self.assertEqual(selected, "Cafe")
        self.assertEqual(component.call_args.kwargs["selected_value"], "Cafe")

    def test_stale_selection_resets_when_option_disappears(self):
        state = {"transaction-picker": "old transaction"}
        with patch.object(
            native_select, "st", SimpleNamespace(session_state=state)
        ), patch.object(
            native_select, "_COMPONENT", return_value="new transaction"
        ) as component:
            selected = native_select.native_selectbox(
                "Transaction",
                ["new transaction", "another transaction"],
                key="transaction-picker"
            )

        self.assertEqual(state["transaction-picker"], "new transaction")
        self.assertEqual(component.call_args.kwargs["selected_value"], "new transaction")
        self.assertEqual(selected, "new transaction")

    def test_placeholder_none_value_is_preserved(self):
        state = {"category-picker": 0}
        with patch.object(
            native_select, "st", SimpleNamespace(session_state=state)
        ), patch.object(
            native_select, "_COMPONENT", return_value=None
        ) as component:
            selected = native_select.native_selectbox(
                "Category",
                [None, "Food"],
                format_func=lambda value: "Choose category" if value is None else value,
                key="category-picker"
            )

        self.assertIsNone(selected)
        self.assertEqual(
            component.call_args.kwargs["options"],
            ["Choose category", "Food"]
        )
        self.assertEqual(component.call_args.kwargs["values"], [None, "Food"])


if __name__ == "__main__":
    unittest.main()
