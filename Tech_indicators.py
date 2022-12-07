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
        pandas.DataFrame: new column for data frame
    """
    return lambda x: x[target].rolling(period).mean().rename(f'SMA {period}')