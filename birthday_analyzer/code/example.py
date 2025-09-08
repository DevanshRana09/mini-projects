from birthday_analyzer.code.display_dates import display_birthdays_with_counts, sort_by_date, sort_by_group_size, \
    sort_by_date_and_name
from birthday_analyzer.code.load_data import load_birthday_data, group_by_birthdate
from pathlib import Path
DATA_FILE = Path(__file__).resolve().parent.parent / "data" / "birthday_data.csv"

def main() -> None:
    """
    Entry point for running the birthday analyzer from the command line.
    """

    data = load_birthday_data(DATA_FILE)

    birthday_groups = group_by_birthdate(data)

    print("🎂 Sorting by date:")
    display_birthdays_with_counts(sort_by_date(birthday_groups))

    print("\n👥 Sorting by group size:")
    display_birthdays_with_counts(sort_by_group_size(birthday_groups))

    print("\n📅 Sorting by date and names:")
    display_birthdays_with_counts(sort_by_date_and_name(birthday_groups))


if __name__ == "__main__":
    main()
