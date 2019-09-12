from django import template
import calendar

register = template.Library()


@register.filter
def month_name(month_number):
    return calendar.month_name[month_number]


@register.filter
def format_number(num, round_to=2):
    num = float(num)
    magnitude = 0
    while abs(num) >= 1000:
        magnitude += 1
        num /= 1000.0
    return '{:.{}f}{}'.format(round(num, round_to), round_to, ['', 'K', 'M', 'G', 'T', 'P'][magnitude])

# @register.filter
# def format_number(num, round_to=1):
#     num_1 = float(num.replace(',', ''))
#     magnitude = 0
#     while abs(num_1) >= 1000:
#         magnitude += 1
#         num_1 = round(num_1 / 1000.0, round_to)
#     return '{:.{}f}{}'.format(round(num_1, round_to), round_to, ['', 'K', 'M', 'G', 'T', 'P'][magnitude])
