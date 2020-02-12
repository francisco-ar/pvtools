# AUTOGENERATED! DO NOT EDIT! File to edit: nbs/03_utils.tmy.ipynb (unless otherwise specified).

__all__ = ['read_pvgis', 'read_tmy']

# Cell
from ..imports import *
import dateutil
import pandas as pd
import pytz

# Cell
def read_pvgis(filename: File, coerce_year: int=None, rename_cols: bool=True):
    "Utility function to read PVGIS tmy files"
    with open(filename, 'r') as csvdata:
        # read in file metadata, advance buffer to second line
        gps_data = {}
        keys = 'Latitude,Longitude,Elevation'.split(',')
        for i in range(3):
            line = csvdata.readline()
            attribute = line.rstrip('\n').split(":")
            gps_data[keys[i]] = float(attribute[1])

        months_year = pd.read_csv(csvdata, nrows=12, engine='python').set_index('month')

        def _parsedate(date_str, year=None):
            "parser to get a coerced year from a tmy file"
            date = pd.datetime.strptime(date_str, '%Y%m%d:%H%M')
            if year is not None:
                date = date.replace(year=year)
            return date


        col_names = 'time(UTC),T2m,RH,G(h),Gb(n),Gd(h),IR(h),WS10m,WD10m,SP'.split(',')
        new_names = 'date,temp,humidity,ghi,dni,dhi,infra,ws,wd,pressure'.split(',')
        date_col = col_names[0]
        data = pd.read_csv(csvdata,
                           header=0,
                           names=col_names,
                           parse_dates=True,
                           date_parser=lambda x: _parsedate(x, year=coerce_year),
                           index_col=date_col,
                           nrows=365*24)
        return gps_data,months_year,data.rename(columns=dict(zip(col_names, new_names)))


# Cell
def read_tmy(filename: File, columns:Optional[list]=None, coerce_year:Optional[int]=None):
    "Reads TMY files with dates on 5 first cols."
    if columns is None:
        columns = ['ghi', 'dni', 'dhi','temp_air', 'temp_dew',
                   'humidity', 'air_pressure','wind_speed', 'wind_dir', 'snow']
    with open(filename, 'r') as csvdata:
        # read in file metadata, advance buffer to second line
        firstline = csvdata.readline().rstrip('\n').split(",")
        secondline = csvdata.readline().rstrip('\n').split(",")
        meta = dict(zip(firstline,secondline))
        meta['Latitude'] = float(meta['Latitude'])
        meta['Longitude'] = float(meta['Longitude'])
        meta['Elevation'] = float(meta['Elevation'])
        meta['Time Zone'] = int(meta['Time Zone'])
        fixed_tz = pytz.FixedOffset(float(meta['Time Zone']) * 60)
        def _parsedate(ymdh, year=None):
            "parser to get a coerced year from a tmy file"
            ymdh = pd.datetime.strptime(ymdh, '%Y %m %d %H %M')
            if year is not None:
                ymdh = ymdh.replace(year=year)
            return ymdh
        data = pd.read_csv(csvdata, header=0,
                           index_col='datetime',
                           parse_dates={'datetime': [0,1,2,3,4]},
                           date_parser=lambda x: _parsedate(x, year=coerce_year)
                          )
        data.columns = columns
        return meta, data.tz_localize(fixed_tz)