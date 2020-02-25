# AUTOGENERATED! DO NOT EDIT! File to edit: nbs/01_utils.pandas_hacks.ipynb (unless otherwise specified).

__all__ = ['group_monthly', 'reindex_monthly_en', 'monthly', 'All', 'mem_usage', 'reduce_mem_usage']

# Cell
from ..imports import *

# Cell
def group_monthly(df: Union[DataFrame, Series], year=2019):
    "Group DataFrame on a monthly basis"
    return (df.groupby([lambda x: x.year, lambda x: x.month]).sum()).loc[year,:]

# Cell
def reindex_monthly_en(data):
    "Rename index to months"
    index=['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun','Jul', 'Aug','Sep', 'Oct', 'Nov', 'Dec']
    if isinstance(data, pd.DataFrame):
        return pd.DataFrame(data.values, index=index, columns=data.columns )
    if isinstance(data, pd.Series):
        return pd.Series(data.values, index=index, name=data.name)

# Cell
def monthly(data, year=2019):
    "Group and reindex a DataFrame or Series monthly"
    return reindex_monthly_en(group_monthly(data, year))

# Cell
def _normalize(df: Union[Series, DataFrame], per_column:bool=False):
    "Scales dataframe to have mean 0 and std 1"
    return (df-df.stack().mean())/df.stack().std() if per_column else (df-df.mean())/df.std()

def _min_max(df: Union[Series, DataFrame], per_column:bool=False):
    "Scales dataframe between 0 and 1"
    return (df-df.stack().min())/(df.stack().max()-df.stack().min()) if per_column else (df-df.min())/(df.max()-df.min())

# Cell
@patch
def normalize(self:DataFrame): return _normalize(self)
@patch
def normalize(self:Series): return _normalize(self)
@patch
def min_max(self:DataFrame): return _min_max(self)
@patch
def min_max(self:Series): return _min_max(self)

# Cell
All = slice(None)

# Cell
def _flatten_cols(df, to_str=True):
    "Flattens the columns MultiIndex"
    df = df.copy()
    flat_cols = df.columns.to_flat_index()
    if to_str:
        df.columns = ['_'.join(c) for c in flat_cols]
    else:
        df.columns = flat_cols
    return df

# Cell
@patch
def flatten_cols(self:DataFrame, to_str=True): return _flatten_cols(self, to_str)

# Cell
def mem_usage(pandas_obj: Union[DataFrame, Series]):
    "Detailed Memory usage of pandas object"
    if isinstance(pandas_obj,pd.DataFrame):
        usage_b = pandas_obj.memory_usage(deep=True).sum()
    else: # we assume if not a df it's a series
        usage_b = pandas_obj.memory_usage(deep=True)
    usage_mb = usage_b / 1024 ** 2 # convert bytes to megabytes
    return f"{usage_mb:03.2f} MB"

def reduce_mem_usage(df: DataFrame, downcast=np.float32, tol:float=1e-7):
    "Downcast float64 to float32 variables on df"
    df_float = df.select_dtypes(include=['float'])
    optimized_df = df.copy()
    optimized_df[df_float.columns] = df_float.astype(dtype=downcast)
    bad_cols = list(df.columns[(optimized_df-df).abs().mean()>tol])
    if len(bad_cols)>0:
        optimized_df.loc[All, bad_cols] = df.loc[All, bad_cols]
        print(f'Columns {bad_cols} where not replaced due to prec. loss')
    return optimized_df