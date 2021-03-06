# AUTOGENERATED! DO NOT EDIT! File to edit: nbs/04_utils.missing.ipynb (unless otherwise specified).

__all__ = ['is_day', 'plot_missing', 'std_outliers', 'diff_outliers', 'comp', 'view_anomaly', 'stuck_outlier',
           'percentile_cutoff', 'MinMaxRemoval']

# Cell
from ..imports import *
from .pandas_hacks import *
from sklearn.base import TransformerMixin

# Cell
def is_day(df: DataFrame, ghi_col='ghi')->DataFrame:
    "Day test, needs ghi col present"
    assert ghi_col in df.columns, f'{ghi_col} is not present'
    return df[df.loc[All, ghi_col]>0]

# Cell
def plot_missing(df: DataFrame, f:Callable[[DataFrame], DataFrame]=pd.isna, ghi_col:Optional[str]=None):
    "Plot data that satisfies the f  function, optional ghi_col to exclude night"
    if ghi_col is not None:
        df = is_day(df, ghi_col)
    cols = df.columns
    n = len(cols)
    _, ax = plt.subplots(figsize=(15,n*0.3))
    outliers = f(df)
    ax.matshow(outliers.T, interpolation=None, aspect='auto')
    xticks = np.arange(0, len(outliers), int(len(outliers)/7))
    ax.set_xticks(xticks)
    ax.set_xticklabels([outliers.index[i].strftime('%d-%m-%Y') for i in xticks])
    ax.set_yticks(range(n))
    ytickslabels = [str(name)+f' ({100*outliers[name].sum()/len(outliers[name]):.3f}%)' for name in cols.values]
    ax.set_yticklabels(ytickslabels)
    return

# Cell
def std_outliers(mean=0, std=1, std_coef=3):
    "Std outlier test func"
    def _inner(df): return (np.abs(df-mean)>std_coef*std)
    return _inner

def diff_outliers(std=1, std_coef=2):
    "Std test on 1st derivative"
    def _inner(df): return (df.diff().abs()>std_coef*std)
    return _inner

# Cell
def comp(l):
    'Compose operator for outlier funcs'
    def _inner(df): return reduce(operator.or_, [f(df) for f in l])
    return _inner

# Cell
def view_anomaly(s: Series, f=std_outliers(0,1,3)):
    "Plots the missing/anomaly points"
    _, ax = plt.subplots(figsize=(14,6))
    a = f(s)
    ax.set_title(f' Anomaly rate: ({100*a.values.sum()/len(s):.3f}%)')
    ax.plot(s, color='blue', label = 'Normal')
    ax.scatter(a[a].index, s[a].fillna(0), color='red', label = 'Anomaly')
    ax.legend()
    return ax

# Cell
def stuck_outlier(tol:float=1e-3, periods=1):
    "Detects if the values are stuck"
    def _inner(df):
        return df.diff().abs().rolling(periods, center=True).max()<tol
    return _inner

# Cell
def percentile_cutoff(data, p_low=5, p_high=95):
    q_low = np.percentile(data,p_low)
    q_high = np.percentile(data, p_high)
    iqr = q_high - q_low
    cut_off = iqr * 1.25
    lower, upper = q_low - cut_off, q_high + cut_off
    return lower, upper

# Cell
class MinMaxRemoval(TransformerMixin):
    "Remove values outside Min-Max within a given tolerance"
    def __init__(self, min_max_tol_dict:dict):
        "A dictionary with the [min, max] interval and a tolerance"
        self.d = min_max_tol_dict

    def fit(self, X, y=None):
        return self

    def transform(self, X:DataFrame, y=None):
        "Apply the transform to your data df"

        X = X.copy()
        for c, val in self.d.items():
            m, M, tol = val
            X[c] = (X[c].mask(np.abs(X[c] - m) < tol, m+tol)  #min replace
                        .mask(np.abs(X[c] - M) < tol, M-tol)  #max replace
                        .where((m - tol < X[c]) & (X[c] < M + tol), np.nan)  #else replace by NaN
                   )
        return X