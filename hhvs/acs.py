import re
from glob import glob

from pandas import DataFrame, read_csv, MultiIndex
from utz import solo

COL_RGX = re.compile(r'(?P<muni>.*) (?:city|borough|town|township), Hudson County, New Jersey!!(?P<type>Estimate|Margin of Error)')


def parse_col(col) -> tuple[str, str]:
    m = COL_RGX.fullmatch(col)
    return m['muni'], m['type']


def load_acs_5y(year: int) -> DataFrame:
    csv_path = solo(glob(f'data/{year}/ACS*5Y{year}*.csv'))
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
    return de
