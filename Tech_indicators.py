def rsi(period:int, target:str = 'midpoint'):
    def rsi(data):
        try:
            up, down = [], []
            for row in data:
                if row > 0:
                    up.append(row)
                elif row < 0:
                    down.append(row)
            up = sum(up)
            down = abs(sum(down))

            return 100-100/(1+down/up)

        except ZeroDivisionError:
            return 100 # If market goes up for all hours causes 0 division error
    return lambda x: x[target].diff().rolling(period).apply(rsi).rename(f'rsi {period}')


def my_rsi(period:int, target:str = 'midpoint'):
    def rsi(data):
        try:
            up, down = [], []
            for row in data:
                if row > 0:
                    up.append(row)
                elif row < 0:
                    down.append(row)
            up = sum(up)
            down = abs(sum(down))

            return 0.5-1/(1+down/up)

        except ZeroDivisionError:
            return 0.5 # If market goes up for all hours causes 0 division error
    return lambda x: x[target].diff().rolling(period).apply(rsi).rename(f'my rsi {period}')


def IHT(target:str = 'midpoint'):
    """In hour trend
    returns the average of the difference in an hour. A basic linear regression.

    Args:
        data (pd.df): hour by hour stock data
    """
    return lambda x: x[target].diff().groupby(x.index).mean().rename('IHT')


def IHTT(target:str = 'midpoint'):
    """In hour trend trend
    returns the average of the difference of the difference in an hour. Sort of a second derivative.

    Args:
        data (pd.df): hour by hour stock data
    """
    return lambda x: x[target].diff().diff().groupby(x.index).mean().rename('IHTT')


def SMA(period:int, target:str = 'midpoint'):
    """Simple Moving Average

    Args:
        period (int): Period of the moving average

    Returns:
        pandas.DataFrame: new column for data frame with name f'{target} SMA {period}'
    """
    return lambda x: x[target].rolling(period).mean().rename(f'{target} SMA {period}')


def midpoint():
    def mid(x):
        x.index = x.index.floor(freq = 'H')
        midd = ((x['low']+x['high'])*0.5)
        midd = midd.groupby(midd.index).mean()
        return midd
    return lambda x: mid(x).rename('midpoint')

def deriv(target):
    """discrete derivative

    Args:
        target (str): column of df

    Returns:
        column of df: Discrete derivative of the data. Column is named f'{target} derivative'
    """
    return lambda x: x[target].diff().rename(f'{target} derivative')

def secondDeriv(target):
    """Discrete second derivative of target column

    Args:
        target (str): name of target column

    Returns:
        df: discrete second derivative of target column named f'{target} second derivative'
    """
    return lambda x: x[target].diff().diff().rename(f'{target} second derivative')

def relative(numerator, denominator):
    """relative

    Normalises a column W.R.T another value

    Args:
        numerator (column): column form df
        denominator (column):column form df

    Returns:
        column: Normalised value named f'relative {numerator}'
    """
    return lambda x: (x[numerator]/x[denominator]).rename(f'relative {numerator}')

def vwap():
    def mid(x):
        x.index = x.index.floor(freq = 'H')
        midd = x['vwap']*x['volume']
        midd = midd.groupby(midd.index).sum()
        volume = x['volume'].groupby(x.index).sum()
        midd = midd/volume
        return midd
    return lambda x: mid(x).rename('vwap')