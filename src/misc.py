def print_separator_line():
    print("===============================")


def get_last_day_of_month(month: int) -> int:
    cases = {
        1: 31,
        2: 28,
        3: 31,
        4: 30,
        5: 31,
        6: 30,
        7: 31,
        8: 31,
        9: 30,
        10: 31,
        11: 30,
        12: 31
    }

    if month not in cases:
        raise Exception("Month must be between 1 and 12")

    return cases[month]
