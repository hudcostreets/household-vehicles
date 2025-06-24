import re
from glob import glob
from os.path import join

import pandas as pd
from pandas import DataFrame, read_csv, MultiIndex
from utz import solo

from hhvs.df import DF
from hhvs.paths import HUDSON

COL_RGX = re.compile(r'(?P<muni>.*) (?:city|borough|town|township), Hudson County, New Jersey!!(?P<type>Estimate|Margin of Error)')


def parse_col(col) -> tuple[str, str]:
    m = COL_RGX.fullmatch(col)
    return m['muni'], m['type']


def tot_veh(df: DF):
    df['Total vehicles'] = df['1 vehicle'] + df['2 vehicles'] * 2 + df['3 vehicles'] * 3 + df['4+ vehicles'] * 4


def hh_veh(df: DF):
    df['Vehicles per household'] = df['Total vehicles'] / df['Total households']


def vehs_df(df: DF):
    df['1-vehicle households'] = df['1 vehicle']
    df['2-vehicle households'] = df['2 vehicles'] * 2
    df['3-vehicle households'] = df['3 vehicles'] * 3
    df['4+-vehicle households'] = df['4+ vehicles'] * 4


class YearDF(DF):
    def __init__(self, year: int):
        csv_path = solo(glob(join(HUDSON, f'data/{year}/ACS*5Y{year}*.csv')))
        d = read_csv(csv_path)
        [ lbl, *cols ] = d.columns.tolist()
        lbl = ('Label', '')
        cols = [ parse_col(col) for col in cols ]
        munis = set([ m for m, _ in cols ])
        dc = d.copy()
        dc.columns = MultiIndex.from_tuples([lbl] + cols)
        dc = dc.iloc[:6].set_index('Label')
        de = dc[[(m, 'Estimate') for m in munis]]
        de.columns = [ m for m, e in de.columns ]
        rows_map = {
            'Total:': "Total households",
            'No vehicle available': '0 vehicles',
            '1 vehicle available': '1 vehicle',
            '2 vehicles available': '2 vehicles',
            '3 vehicles available': '3 vehicles',
            '4 or more vehicles available': '4+ vehicles',
        }
        rows = [ r.strip() for r in de.index ]
        assert rows == list(rows_map.keys())
        de.index = list(rows_map.values())
        de.columns.name = 'Municipality'
        de = (
            de
            .transpose()
            .map(lambda s: s.replace(',', '') if isinstance(s, str) else s)
            .astype(int)
        )
        tot_veh(de)
        hh_veh(de)
        vehs_df(de)
        super().__init__(de)


class YearsDF(DF):
    def __init__(self, first: int = 2016, last: int = 2023):
        d = (
            pd.concat([
                YearDF(year).df.assign(year=year)
                for year in range(first, last + 1)
            ])
            .reset_index()
            .set_index(['year', 'Municipality'])
        )
        hh_veh(d)
        super().__init__(d)
