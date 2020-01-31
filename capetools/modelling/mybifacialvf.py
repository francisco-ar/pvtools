# AUTOGENERATED! DO NOT EDIT! File to edit: nbs/06_modelling.mybifacialvf.ipynb (unless otherwise specified).

__all__ = ['CHAMBERY', 'get_tmy3', 'format_output']

# Cell
import bifacialvf

# Cell
CHAMBERY = {'Name':'Chambery', 'latitude': 45.637001, 'longitude': 5.881, 'Elevation': 235.0, 'TZ':-1.0}

# Cell
def get_tmy3(data):
    "Rename to upper case dni and ghi cols"
    tmy3 = (data[['dni', 'dhi', 'zenith', 'azimuth', 'elevation']]
            .rename(columns={'dni':'DNI', 'dhi':'DHI'}))
    return tmy3

# Cell
def format_output(res, cuts):

    front_cols = [f'No_{i+1}_RowFrontGTI' for i in range(cuts)]
    back_cols = [f'No_{i+1}_RowBackGTI' for i in range(cuts)]
    aux = pd.DataFrame(index=res.index)
    aux['qinc_front'] = res[front_cols].mean(axis=1)
    aux['qinc_back_mean'] = res[back_cols].mean(axis=1)
    aux[back_cols] = res[back_cols]
    aux =  aux.rename(columns=dict(zip(back_cols,[f'qinc_back_{i}' for i in range(cuts-1, -1, -1)] )))
    return aux[['qinc_front', 'qinc_back_mean']+[f'qinc_back_{i}' for i in range(cuts)]]