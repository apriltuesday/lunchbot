import datetime
import os
import re

import pdfplumber
import requests


base_url = 'https://food-rewards.com/wp-content/uploads/'
tmp_file = '/tmp/menu.pdf'

days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']


def get_filepath(date: datetime.date):
    year = date.year
    month = date.month
    day = date.day
    ones = day % 10
    if ones == 1:
        suffix = 'st'
    elif ones == 2:
        suffix = 'nd'
    elif ones == 3:
        suffix = 'rd'
    else:
        suffix = 'th'
    weekday = days[date.weekday()]
    calmonth = months[month-1]
    return f'{year}/{month:02}/{weekday}-{day}{suffix}-{calmonth}-{year}.pdf'


def normalise_whitespace(s):
    return ' '.join(s.split())


def process_allergens(allergens):
    allergens = normalise_whitespace(allergens).replace('TREE NUTS', 'tree-nuts')
    processed = [x.strip().capitalize() for x in re.split(', | ', allergens)]
    if not processed or processed == ['']:
        return []
    return processed


def get_menu(date):
    """Get menu for a given date"""
    response = requests.get(os.path.join(base_url, get_filepath(date)))
    response.raise_for_status()

    with open(tmp_file, 'wb') as f:
        f.write(response.content)

    f = pdfplumber.open(tmp_file)
    table = f.pages[0].extract_table()
    all_items = []
    all_allergens = []
    all_may_contains = []

    # skip header/footer rows
    for row in table[2:-1]:
        # whitespace normalisation
        item = normalise_whitespace(row[0])
        if ' - 1 Serving' not in item:
            continue
        item = item[:item.index(' - 1 Serving')].strip().capitalize()
        allergens = process_allergens(row[2])
        may_contains = process_allergens(row[3])
        all_items.append(item)
        all_allergens.append(allergens)
        all_may_contains.append(may_contains)

    return all_items, all_allergens, all_may_contains


if __name__ == '__main__':
    # for testing
    items, allergens, may_contains = get_menu(datetime.date.today())
    print(items)
    print(allergens)
    print(may_contains)
