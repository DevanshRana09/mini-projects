from datetime import datetime
from typing import Dict, List


def display_birthdays(birthday_dict: Dict[str, List[str]]) -> None:
    """
    Print each date with corresponding names.
    """
    for date, names in birthday_dict.items():
        print(f"{date}: {', '.join(names)}")


def display_birthdays_with_counts(birthday_dict: Dict[str, List[str]]) -> None:
    """
    Print each date, count of people, and list of names.
    """
    for date, names in birthday_dict.items():
        print(f"\n{date} ({len(names)} people):")
        print(names)


def sort_by_date(birthday_dict: Dict[str, List[str]]) -> Dict[str, List[str]]:
    """
    Sort birthdays chronologically (Jan -> Dec).
    """
    return dict(sorted(
        birthday_dict.items(),
        key=lambda x: datetime.strptime(x[0], "%b %d")
    ))


def sort_by_group_size(birthday_dict: Dict[str, List[str]]) -> Dict[str, List[str]]:
    """
    Sort birthdays by number of people (largest first).
    """
    return dict(sorted(
        birthday_dict.items(),
        key=lambda x: len(x[1]),
        reverse=True
    ))


def sort_by_date_and_name(birthday_dict: Dict[str, List[str]]) -> Dict[str, List[str]]:
    """
    Sort birthdays chronologically and sort names alphabetically within each date.
    """
    sorted_dict: Dict[str, List[str]] = {}
    for date, names in sorted(
        birthday_dict.items(),
        key=lambda x: datetime.strptime(x[0], "%b %d")
    ):
        sorted_dict[date] = sorted(names)
    return sorted_dict
