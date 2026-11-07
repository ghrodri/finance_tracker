from db import execute, fetch
from utils import add_months


def entries_for_month(ym):
    return fetch("entries_for_month", (ym, ym, ym))


def add_entry(kind, name, category, amount, ym, recurring):
    execute("insert_entry", (kind, name, category, round(amount, 2), ym, None, 1 if recurring else 0))


def update_entry_amount(entry_id, ym, amount):
    # a monthly item changes from this month on, older months keep the old amount
    found = fetch("get_entry", (entry_id,))
    if not found:
        return
    entry = found[0]
    amount = round(amount, 2)
    if not entry["recurring"] or entry["start_month"] >= ym:
        execute("update_entry_amount", (amount, entry_id))
        return
    execute("end_entry", (add_months(ym, -1), entry_id))
    execute(
        "insert_entry",
        (entry["kind"], entry["name"], entry["category"], amount, ym, entry["end_month"], 1),
    )


def remove_entry(entry_id, ym):
    # one-time items are deleted, monthly items just stop from this month on
    found = fetch("get_entry", (entry_id,))
    if not found:
        return
    entry = found[0]
    if not entry["recurring"] or entry["start_month"] >= ym:
        execute("delete_entry", (entry_id,))
    else:
        execute("end_entry", (add_months(ym, -1), entry_id))
