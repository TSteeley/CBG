import pickle
import pandas as pd
from math import inf
import random
from numpy import clip
from Gather_data import Gather
pd.options.mode.chained_assignment = None

class CBG:
    def __init__(self):
        self.instruments = {}
        self.intra_indicators = []
        self.inter_indicators = []
        self.trigger_condition = ''
        self.buyPrice = ''
        self.win_condition = ''
        self.fail_condition = ''
        self.report = {}
        self.positions = {}

    def set_instruments(self, instruments:list, intra_indicators:list = [], inter_indicators:list = []):
        """Initialise data

        premade indicators can be found in Tech_indicators file

        Args:
            instruments (list): list of instruments by name [qqq,spy,...]
            intra_indicators (list, optional): intra hour indicators, input lambda functions. Defaults to [].
            inter_indicators (list, optional): inter hour indicators, input lambda functions. Defaults to [].

        Returns:
            pd.df : all data with indicators
        """
        self.inter_indicators = inter_indicators
        self.intra_indicators = intra_indicators
# open	high	low	close	volume	trade_count	vwap
        all_data = pickle.load(open('data.pkl','rb'))
        for ins in instruments:
            use = pd.DataFrame()
            data:pd.DataFrame = all_data[f'{ins}']
            data.index = data.index.floor('H')
            use['high'] = data['high'].groupby(data.index).max()
            use['low'] = data['low'].groupby(data.index).min()
            use['close'] = data['close'].groupby(data.index).nth(-1)

            for ind in intra_indicators:
                use = pd.DataFrame.join(use,ind(data))

            for ind in inter_indicators:
                use = pd.DataFrame.join(use,ind(use))

            self.instruments[f'{ins}'] = use.dropna()
        return self

    def set_trigger(self, condition):
        """trigger condition
        i.e. under what condition should a buy be excuted.

        pass in a lambda fuction that returns true when a buy should be executed
        """
        self.trigger_condition = condition
        return self

    def set_buyPrice(self, condition):
        """Set buy price

        given the conditions at what price should the position be bought at.

        pass in a lambda function that returns a value within the upper and lower bound of the time period

        """
        self.buyPrice = condition
        return self

    def set_wlCondition(self, Win_condition, Fail_condition):
        """set win and loss condiiton

        pass in 2 lambda funcitons. the first given the conditions should assess how high to shoot for and return a value for upper bound. the second should return a lower value or stop loss equivalent
        """
        self.win_condition = Win_condition
        self.fail_condition = Fail_condition
        return self


    def execute_buys(self):
        """# Execute Buy

        Using the given conditions runs through every instrument being monitored and creates a list of dictionaries.
        [time, Buy Price, Target Price, Fail Price]

        This is the first step in executing the model, broken up so I dont gouge my on eyes out
        """
        for ins in self.instruments:
            triggers = self.trigger_condition(self.instruments[ins])
            triggers['Buy Price'] = self.buyPrice(triggers)
            triggers['TP'] = self.win_condition(triggers)
            triggers['SL'] = self.fail_condition(triggers)
            triggers.loc[triggers['Buy Price'] > triggers['TP'], 'TP'] = triggers['Buy Price']*1.05
            triggers.loc[triggers['Buy Price'] < triggers['SL'], 'SL'] = triggers['Buy Price']*0.95
            self.positions[ins] = triggers.loc[:,['Buy Price','TP','SL']]
        return self


    def assess_outcome(self):
        for ind in self.positions:
            outcomes = []
            for pos in self.positions[ind].reset_index().to_dict('records'):
                period = self.instruments[ind].loc[pos['timestamp']:pos['timestamp']+pd.Timedelta(days=7),:]
                # IF the price never reaches the take profit or stop loss; 0 hits
                if all([pos['SL'] < i < pos['TP'] for i in [period['low'].min(), period['high'].max()]]):
                    outcomes.append({
                        'timestamp': pos['timestamp'],
                        'outcome' : 'Too Old',
                        'close price' : period.iloc[-1,:]['close']
                    })
                # IF the price reaches the Take profit AND stop loss; Mulitple hits
                elif not any([pos['SL'] < i < pos['TP'] for i in [period['low'].min(), period['high'].max()]]):
                    # comb through hour by hour to see what happens first
                    close = period[(period['high'] > pos['TP']) | (period['low'] < pos['SL'])].iloc[0,:]
                    if close['low'] < pos['SL']:
                        outcomes.append({
                            'timestamp' : pos['timestamp'],
                            'outcome' : 'Fail',
                            'close price' : pos['SL']
                        })
                    elif close['high'] > pos['TP']:
                        outcomes.append({
                            'timestamp' : pos['timestamp'],
                            'outcome' : 'Success',
                            'close price' : pos['TP']
                    })

                # IF the price only reaches the Take profit
                elif period['high'].max() > pos['TP']:
                    outcomes.append({
                        'timestamp' : pos['timestamp'],
                        'outcome' : 'Success',
                        'close price' : pos['TP']
                    })

                # IF the price reaches the Stop loss
                elif period['low'].min() < pos['SL']:
                    outcomes.append({
                        'timestamp' : pos['timestamp'],
                        'outcome' : 'Fail',
                        'close price' : pos['SL']
                    })
                    # assign close to be stop loss price
                else:
                    print('Somethings fucked')
            self.positions[ind] = pd.DataFrame.join(self.positions[ind],pd.DataFrame(outcomes).set_index('timestamp'))


    def get_score(self):
        score = []
        for pos in self.positions:
            scr = (self.positions[pos]['close price']/self.positions[pos]['Buy Price'])
            scr = scr-1
            scr = scr.sum()
            score.append(scr)
        return sum(score)/len(score)

    def get_report(self):
        gap = ' | '
        headings = f"{gap}{'Wins':4s}{gap}{'Fails':5s}{gap}{'Closed':6s}{gap}{'Closed Average':14s}{gap} "
        print('='*43)
        for idx, pos in enumerate(self.positions):
            outcomes = self.positions[pos].groupby(self.positions[pos]['outcome']).size()
            closes = self.positions[pos][self.positions[pos]['outcome'] == 'Too Old']
            closes = closes['close price']/closes['Buy Price']-1
            print(pos)
            print(headings)
            a = lambda x: 0 if x not in outcomes else outcomes[x]
            print(f"{gap}{a('Success'):4d}{gap}{a('Fail'):5d}{gap}{a('Too Old'):6d}{gap}{closes.mean():14.7f}{gap}")
            score = (self.positions[pos]['close price']/self.positions[pos]['Buy Price']-1).sum()
            print(f'Score: {score}')
        print('='*43)

