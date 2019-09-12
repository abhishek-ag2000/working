"""
Utility and Business Logic
"""


def calculate_price(monthly_price, quarterly_price, half_yearly_price, annual_price, month_count):
    """
    Returns product price based on month count and different prices
    """
    if month_count < 1:
        return 0

    if month_count < 3:
        return round(monthly_price * month_count, 0)

    if month_count < 6:
        return round(quarterly_price / 3 * month_count, 0)

    if month_count < 12:
        return round(half_yearly_price / 6 * month_count, 0)

    return round(annual_price / 12 * month_count, 0)
