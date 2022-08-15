from time import sleep
import pandas as pd
import pickle
from alpha_vantage.timeseries import TimeSeries
from api_key import av_key

api_key = av_key

def Gather(ticker, new_data=False, stage:str = 'training'):
    if not new_data:
        match stage:
            case 'training':
                data = pickle.load(open(f'./training_data.pkl', 'rb'))[ticker]
            case 'verifying':
                data = pickle.load(open(f'./data.pkl', 'rb'))[ticker]
    else:
        old_data = pickle.load(open('data.pkl', 'rb'))
        data = pd.DataFrame()
        ts = TimeSeries(key=api_key, output_format='csv')
        for y in range(1, 3):
            for m in range(1, 13):
                # this section is marked for imporvement
                # AV has a ratelimit of 5/ min so I just have it wait 12 seconds between
                # calls. it doesnt feel particularly efficient but it works for now.

                sleep(12)
                data_ts, meta_data = ts.get_intraday_extended(
                    symbol=ticker, interval='1min', slice=f'year{str(y)}month{str(m)}')
                part = pd.DataFrame(data_ts)
                part.columns = part.iloc[0, :]
                part['time'] = pd.to_datetime(part['time'], errors='coerce')
                for col in part.iloc[:, 1::]:
                    part[col] = pd.to_numeric(part[col], errors='coerce')
                part = part.set_index('time')
                data = pd.concat([data,part])
        data.columns = ['2. high', '3. low', '4. close']
        data['midpoint'] = ((data['2. high']+data['3. low'])*0.5)
        data = data.sort_index(ascending=True)
        old_data[f'{ticker}_raw'] = data
        calculated_data = Calculate(data)
        old_data[f'{ticker}'] = calculated_data
        pickle.dump(old_data, open(f'data.pkl', 'wb'))
    return data

def Calculate(data: pd.DataFrame):
    """# Calculate

    All data interpretation in one place for easier bug finding.

    Not necessarily meant to be directly called.

    Args:
        data(pandas.DataFrame): raw data downloaded from Alpha Vantage

    Returns:
        list[dictionary]: List of dictionaries for intepretation
    """
    # main data
    data.index = data.index.floor('H')
    b = data['2. high'].groupby(data.index).max()
    c = data['3. low'].groupby(data.index).min()
    c1 = data['4. close'].groupby(data.index).nth(-1)
    d = data['midpoint'].groupby(data.index).mean()
    # intra hour indicators
    d1 = data['midpoint'].groupby(data.index).std().rename('standard deviation')
    e = data['midpoint'].diff().groupby(data.index).mean().rename('iht') # in hour trend
    f = data['midpoint'].diff().diff().groupby(data.index).mean().rename('ihtt') # trend of the in hour trend sort of
    # concatenate into hour by hour data
    data = pd.concat([b, c, c1, d, d1, e, f], axis=1).dropna()
    # at 8pm every day 1 data point goes through for the hour. This returns na in std and breaks my shit. dropna() fixes that
    data['rolling intra std'] = (data['standard deviation'].rolling(20).mean())/data['midpoint'] # expressed as a %
    data['rolling inter std'] = data['standard deviation']/data['midpoint'] # expressed as a %
    data['sma 100'] = data['midpoint'].rolling(100).mean()
    data['sma 100 dirv smooth'] = data['sma 100'].diff().rolling(7).mean()
    data['sma 100 ddirv smooth'] = data['sma 100'].diff().diff().rolling(20).mean()
    data['sma 20'] = data['midpoint'].rolling(20).mean()
    data['sma 20 dirv smooth'] = data['sma 20'].diff().rolling(7).mean()
    data['sma 20 ddirv smooth'] = data['sma 20'].diff().diff().rolling(20).mean()
    data['rsi'] = data['midpoint'].diff().rolling(14).apply(my_rsi)
    data['rsi dirv smooth'] = data['rsi'].diff().rolling(7).mean()
    data['rsi ddirv smooth'] = data['rsi'].diff().diff().rolling(20).mean()
    data['20,100 gap'] = (data['sma 20']-data['sma 100'])*data['sma 100']
    data['mp, 20 gap'] = (data['midpoint']-data['sma 20'])*data['sma 20']
    data['mp,100 gap'] = (data['midpoint']-data['sma 100'])*data['sma 100']

    data.to_csv('wtf.csv')
    data = data.dropna()
    data = data.reset_index()
    data = data.to_dict('records')
    return data


def reinterprate(ticker: str = '0'):
    """#Reinterparate
    Alpha vantage rate limit makes downloading datasets time consuming
    this file stores a raw data set that can be reintepereated if indicators are to be added
    or removed.

    Args:
        ticker (str): stock identifier/ ticker

    Returns:
        pandas.DataFrame
    """
    data = pickle.load(open(f'./data.pkl', 'rb'))
    if ticker == '0':
        ticker = get_tickers()
    for tick in ticker:
        data[tick] = Calculate(data[f'{tick}_raw'])
    pickle.dump(data, open(f'data.pkl', 'wb'))
    return data


def my_rsi(data):
    """# My RSI

    RSI seems to be one of the better indicators from my testing but a number from 0-100 is not useul to me,
    this gives a value from -0.5 to 0.5m instead.

    otherwise it uses the same method as regular RSI

    Args:
        data (pd.): _description_

    Returns:
        int: RSI value from -0.5 - 0.5
    """
    try:
        up, down = [], []
        for row in data:
            if row > 0:
                up.append(row)
            elif row < 0:
                down.append(row)
        up = sum(up)
        down = sum(down)

        return 0.50-1/(1-up/down)

    except ZeroDivisionError:
        return 0.5 # If market goes up for all hours causes 0 division error

def get_tickers(stage:str = 'training'):
    match stage:
        case 'training':
            data:dict = pickle.load(open(f'training_data.pkl', 'rb'))
        case 'verifying':
            data:dict = pickle.load(open(f'data.pkl', 'rb'))
    important_keys = []
    for i in data:
        if not i.__contains__('_raw'):
            important_keys.append(i)
    return important_keys
