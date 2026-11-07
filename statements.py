from collections import defaultdict
from datetime import date

from config import START_DATE
from db import fetch
from utils import add_months, month_first, month_last, parse_iso, ym_of


def build_statement(acc, txs, upto_ym, today=None):
    # monthly rows from the account's first month up to upto_ym.
    # interest uses the daily balance of every day in the month
    today = today or date.today()
    open_d = max(parse_iso(acc["open_date"]) or START_DATE, START_DATE)
    compound = acc["type"] != "fixed"
    can_auto = bool(acc["auto_interest"]) and acc["type"] in ("savings", "fixed") and acc["rate"] > 0
    rate = acc["rate"] / 100.0

    by_day = defaultdict(list)
    for tx in txs:
        by_day[tx["date"]].append(tx)

    principal = float(acc["opening_balance"])
    accrued = 0.0
    result = {}
    ym = ym_of(open_d)
    while ym <= upto_ym:
        first, last = month_first(ym), month_last(ym)
        ndays = last.day
        opening = principal + accrued
        deposits = withdrawals = fees = adjustments = manual = 0.0
        has_manual = False
        base_sum = 0.0
        days = 0
        daily = []

        d = max(first, open_d)
        while d <= last:
            for tx in by_day.get(d.isoformat(), []):
                kind, amount = tx["kind"], tx["amount"]
                if kind == "deposit":
                    principal += amount
                    deposits += amount
                elif kind == "withdrawal":
                    withdrawals += amount
                    # accrued interest goes out first
                    from_accrued = min(accrued, amount)
                    accrued -= from_accrued
                    principal -= amount - from_accrued
                elif kind == "fee":
                    principal -= amount
                    fees += amount
                elif kind == "adjustment":
                    principal += amount
                    adjustments += amount
                elif kind == "interest":
                    manual += amount
                    has_manual = True
            base_sum += principal
            days += 1
            daily.append((d.day, principal + accrued))
            d = date.fromordinal(d.toordinal() + 1)

        auto = 0.0
        if can_auto and days:
            if acc["basis"] == "act360":
                auto = base_sum * rate / 360.0
            elif acc["basis"] == "avg12":
                auto = (base_sum / ndays) * rate / 12.0
            else:
                auto = base_sum * rate / 365.0
        auto = round(auto, 2)

        # interest reported by the bank wins over the estimate
        if has_manual:
            interest, source = round(manual, 2), "bank"
        elif auto:
            interest, source = auto, "auto"
        else:
            interest, source = 0.0, "none"

        if compound:
            principal += interest
        else:
            accrued += interest
        principal = round(principal, 2)
        accrued = round(accrued, 2)

        result[ym] = {
            "opening": round(opening, 2),
            "deposits": round(deposits, 2),
            "withdrawals": round(withdrawals, 2),
            "interest": interest,
            "fees": round(fees, 2),
            "adjustments": round(adjustments, 2),
            "closing": round(principal + accrued, 2),
            "avg": (base_sum / days) if days else 0.0,
            "days": days,
            "source": source,
            "auto": auto,
            "manual": round(manual, 2) if has_manual else None,
            "projected": last >= today,
            "daily": daily,
        }
        ym = add_months(ym, 1)
    return result


def statements(upto_ym):
    # (account, monthly rows) for every account
    by_account = defaultdict(list)
    for tx in fetch("all_transactions"):
        by_account[tx["account_id"]].append(tx)
    return [(acc, build_statement(acc, by_account[acc["id"]], upto_ym)) for acc in fetch("all_accounts")]
