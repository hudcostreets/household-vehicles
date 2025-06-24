import pandas as pd


class DF:
    def __init__(self, df: pd.DataFrame):
        self.df = df

    def __getattr__(self, item):
        return getattr(self.df, item)

    def __setattr__(self, key, value):
        if key == 'df':
            super().__setattr__(key, value)
        else:
            setattr(self.df, key, value)

    def __getitem__(self, item):
        return self.df[item]

    def __setitem__(self, key, value):
        self.df[key] = value

    def __repr__(self):
        return self.df.__repr__()

    def __str__(self):
        return self.df.__str__()
