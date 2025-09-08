import pandas as pd
from pandas import DataFrame
from collections import defaultdict
from typing import Dict, List


def load_birthday_data(csv_path: str, sep: str = ",") -> DataFrame:
    """
    Load birthday data from a CSV file.

    Parameters
    ----------
    csv_path : str
        Path to the CSV file containing 'name' and 'date' columns.
    sep : str, optional
        Separator used in the CSV file (default is comma).

    Returns
    -------
    pd.DataFrame
        DataFrame with columns 'name' and 'date'.
    """
    return pd.read_csv(csv_path, sep=sep)


def group_by_birthdate(data: DataFrame) -> Dict[str, List[str]]:
    """
    Group people who share the same birthday.

    Parameters
    ----------
    data : pd.DataFrame
        A DataFrame with 'name' and 'date' columns.

    Returns
    -------
    dict[str, list[str]]
        Dictionary mapping dates to lists of names.
    """
    birthday_map: Dict[str, List[str]] = defaultdict(list)
    for row in data.itertuples(index=False):
        birthday_map[row.date].append(row.name)
    return birthday_map

