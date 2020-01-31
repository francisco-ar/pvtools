# AUTOGENERATED! DO NOT EDIT! File to edit: nbs/06_modelling.mybifacialvf.ipynb (unless otherwise specified).

__all__ = ['get_tmy3', 'CHAMBERY']

# Cell
import bifacialvf

# Cell
CHAMBERY = {'Name':'Chambery', 'latitude': 45.637001, 'longitude': 5.881, 'Elevation': 235.0, 'TZ':-1.0}

def get_tmy3(data):
    tmy3 = (data[['dni', 'dhi', 'zenith', 'azimuth', 'elevation']]
            .rename(columns={'dni':'DNI', 'dhi':'DHI'}))
    return tmy3