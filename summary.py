from config import TYPE_LABEL
from entries import entries_for_month
from statements import statements


def month_summary(ym):
    sts = statements(ym)
    by_type = {kind: 0.0 for kind in TYPE_LABEL}
    deposits = withdrawals = interest = fees = 0.0
    for acc, rows in sts:
        row = rows.get(ym)
        if row:
            by_type[acc["type"]] += row["closing"]
            deposits += row["deposits"]
            withdrawals += row["withdrawals"]
            interest += row["interest"]
            fees += row["fees"]

    entries = entries_for_month(ym)
    income = sum(e["amount"] for e in entries if e["kind"] == "income")
    expenses = sum(e["amount"] for e in entries if e["kind"] == "expense")
    saved = deposits - withdrawals
    return {
        "sts": sts,
        "by_type": by_type,
        "nw": sum(by_type.values()),
        "deposits": deposits,
        "withdrawals": withdrawals,
        "saved": saved,
        "interest": interest,
        "fees": fees,
        "entries": entries,
        "income": income,
        "expenses": expenses,
        "left": income - expenses - saved,
    }
