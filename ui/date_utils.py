from datetime import date, datetime
from zoneinfo import ZoneInfo


APP_TIMEZONE = ZoneInfo("Asia/Kolkata")
TRANSACTION_DATE_KEY = "add_transaction_date"
LAST_TRANSACTION_DATE_DAY_KEY = "_last_transaction_date_day"


def current_app_date() -> date:
    return datetime.now(APP_TIMEZONE).date()


def transaction_date_needs_rollover(session_state, current_date: date) -> bool:
    return session_state.get(LAST_TRANSACTION_DATE_DAY_KEY) != current_date


def sync_transaction_date(session_state, current_date: date) -> bool:
    if not transaction_date_needs_rollover(session_state, current_date):
        return False

    session_state[LAST_TRANSACTION_DATE_DAY_KEY] = current_date
    session_state[TRANSACTION_DATE_KEY] = current_date
    return True
