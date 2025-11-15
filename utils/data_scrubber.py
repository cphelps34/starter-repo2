import pandas as pd


class DataScrubber:
    """Minimal DataScrubber stub with a remove_duplicate_records method.

    This is a simplified implementation so the example scripts can run.
    """

    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()

    def remove_duplicate_records(self) -> pd.DataFrame:
        # Very simple duplicate removal: drop fully duplicate rows
        return self.df.drop_duplicates()
