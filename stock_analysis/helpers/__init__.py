from datetime import datetime


def get_daily_investment(daily_investment_pairs: list[tuple[datetime, int]], date):
    # Sort and find the appropriate investment amount
    daily_investment_pairs.sort()
    investment_amount = None
    for invest_date, amount in daily_investment_pairs:
        if invest_date <= date:
            investment_amount = amount
        else:
            break
    return investment_amount
