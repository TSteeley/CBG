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

        all_data = pickle.load(open('data.pkl','rb'))
        for ins in instruments:
            use = pd.DataFrame()
            data:pd.DataFrame = all_data[f'{ins}_raw']
            use['high'] = data['2. high'].groupby(data.index).max()
            use['low'] = data['3. low'].groupby(data.index).min()
            use['close'] = data['4. close'].groupby(data.index).nth(-1)
            use['midpoint'] = data['midpoint'].groupby(data.index).mean()

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
                period = self.instruments[ind].loc[pos['time']:pos['time']+pd.Timedelta(days=7),:]
                # IF the price never reaches the take profit or stop loss; 0 hits
                if all([pos['SL'] < i < pos['TP'] for i in [period['low'].min(), period['high'].max()]]):
                    outcomes.append({
                        'time': pos['time'],
                        'outcome' : 'Too Old',
                        'close price' : period.iloc[-1,:]['close']
                    })
                # IF the price reaches the Take profit AND stop loss; Mulitple hits
                elif not any([pos['SL'] < i < pos['TP'] for i in [period['low'].min(), period['high'].max()]]):
                    # comb through hour by hour to see what happens first
                    close = period[(period['high'] > pos['TP']) | (period['low'] < pos['SL'])].iloc[0,:]
                    if close['low'] < pos['SL']:
                        outcomes.append({
                            'time' : pos['time'],
                            'outcome' : 'Fail',
                            'close price' : pos['SL']
                        })
                    elif close['high'] > pos['TP']:
                        outcomes.append({
                            'time' : pos['time'],
                            'outcome' : 'Success',
                            'close price' : pos['TP']
                    })

                # IF the price only reaches the Take profit
                elif period['high'].max() > pos['TP']:
                    outcomes.append({
                        'time' : pos['time'],
                        'outcome' : 'Success',
                        'close price' : pos['TP']
                    })

                # IF the price reaches the Stop loss
                elif period['low'].min() < pos['SL']:
                    outcomes.append({
                        'time' : pos['time'],
                        'outcome' : 'Fail',
                        'close price' : pos['SL']
                    })
                    # assign close to be stop loss price
                else:
                    print('Somethings fucked')
            self.positions[ind] = pd.DataFrame.join(self.positions[ind],pd.DataFrame(outcomes).set_index('time'))

    def assess_outcome1(self):
        for ind in self.positions:
            outcomes = []
            for pos in self.positions[ind].reset_index().to_dict('records'):
                period:pd.DataFrame = self.instruments[ind].loc[pos['time']:pos['time']+pd.Timedelta(days=7),:]
                # IF the price never reaches the take profit or stop loss; 0 hits
                if all([pos['SL'] < i < pos['TP'] for i in [period['low'].min(), period['high'].max()]]):
                    outcomes.append({
                        'time': pos['time'],
                        'close price' : period.iloc[-1,:]['close']
                    })
                else:
                    close = period[(period['high'] > pos['TP']) | (period['low'] < pos['SL'])].iloc[0,:]
                    if close['low'] < pos['SL']:
                        outcomes.append({
                            'time' : pos['time'],
                            'close price' : pos['SL']
                        })
                    elif close['high'] > pos['TP']:
                        outcomes.append({
                            'time' : pos['time'],
                            'close price' : pos['TP']
                        })
            self.positions[ind] = pd.DataFrame.join(self.positions[ind], pd.DataFrame(outcomes).set_index('time'))
        return self

    def get_score(self):
        score = []
        for pos in self.positions:
            scr = (self.positions[pos]['close price']/self.positions[pos]['Buy Price'])
            scr = scr-1
            scr = scr.sum()
            score.append(scr)
        return sum(score)/len(score)

    def get_report(self):
        for pos in self.positions:
            print(self.positions[pos].groupby(self.positions[pos]['outcome']).size())
            a = self.positions[pos].loc[self.positions[pos]['outcome'] == 'Too Old']
            a = ((a['Buy Price']/a['close price'])-1).sum()
            print(f'Too Old closed with an average gain of {a}')


# class old:
#     def __init__(self, data, stage):
#         self.history = []
#         self.open = []
#         self.max_positions = inf
#         self.age_limit = 200
#         self.score = -inf
#         self.id = ''

#     def update_args(self, vars:list):
#         self.score = []
#         self.args = vars
#         self.target = vars[0]
#         self.fail = vars[1]
#         count = 2

#         for part in [self.price_modifiers, self.w_modifier, self.f_modifier]:
#             for item in part:
#                 part[item] = vars[count]
#                 count+=1

#         return self

#     def Update_Price(self, data):
#         self.buy = data[self.basis]
#         modifier = 1
#         for key in self.price_modifiers:
#             modifier += data[key]*self.price_modifiers[key]

#         self.buy *= modifier
#         return self

#     def buy_order(self, data):
#         buy , sell = 1, 1

#         for key in self.w_modifier:
#             buy += data[key]*self.w_modifier[key]
#         for key in self.f_modifier:
#             sell+= data[key]*self.f_modifier[key]

#         buy = max(1, buy + self.target)
#         sell=  clip(sell-self.fail,0,1)

#         self.open.append({
#             'time': data['time'],
#             'age':0,
#             'type': 'Buy',
#             'Price':self.buy,
#             'win': self.buy*buy,
#             'fail': self.buy*sell
#         })
#         return self

#     def check_closes(self, data):
#         if self.open.__len__() == 0:
#             return self

#         close = [d for d in self.open if (d['type'] == 'Buy') & ((d['win'] < data['2. high']) | (d['fail'] > data['3. low']) | (d['age'] >= self.age_limit))]

#         for row in close:
#             if ambiguous(row, data):
#                 self.history.append({
#                     'Open Time': row['time'],
#                     'Close Time': data['time'],
#                     'type': row['type'],
#                     'Price':row['Price'],
#                     'Close': 0,
#                     'Outcome': 'Ambiguous'
#                 })
#                 self.open.remove(row)

#             elif win(row, data):
#                 self.history.append({
#                     'Open Time': row['time'],
#                     'Close Time': data['time'],
#                     'type': row['type'],
#                     'Price':row['Price'],
#                     'Close': row['win'],
#                     'Outcome': 'Success'
#                 })
#                 self.open.remove(row)

#             elif fail(row, data):
#                 self.history.append({
#                     'Open Time': row['time'],
#                     'Close Time': data['time'],
#                     'type': row['type'],
#                     'Price':row['Price'],
#                     'Close': row['fail'],
#                     'Outcome': 'Fail'
#                 })
#                 self.open.remove(row)

#             elif row['age'] >= self.age_limit:
#                 self.history.append({
#                     'Open Time': row['time'],
#                     'Close Time': data['time'],
#                     'type': row['type'],
#                     'Price':row['Price'],
#                     'Close': data['4. close'],
#                     'Outcome': 'Too Old'
#                 })
#                 self.open.remove(row)
#         for row in self.open:
#             row['age'] += 1
#         return self

#     def closing_time(self):
#         for row in self.open:
#             if row['age'] <= self.age_limit:
#                 self.history.append({
#                     'Open Time': row['time'],
#                     'Close Time': 'N/A',
#                     'type': row['type'],
#                     'Price':row['Price'],
#                     'Outcome': 'just a baby'
#                 })
#                 self.open.remove(row)
#             else:
#                 self.history.append({
#                     'Open Time': row['time'],
#                     'Close Time': 'N/A',
#                     'type': row['type'],
#                     'Price':row['Price'],
#                     'Outcome': 'remains open'
#                 })
#                 self.open.remove(row)
#         return self

#     def get_open_positions(self):
#         return self.open.__len__()

#     def get_keys(self):
#         keys = []
#         for part in [self.price_modifiers, self.w_modifier, self.f_modifier]:
#             key = []
#             for item in part:
#                 key.append(item)
#             keys.append(keys)
#         return keys

#     def set_id(modifiers):
#         b = str(modifiers[0].keys()).removeprefix('dict_keys(').removesuffix(')')
#         c = str(modifiers[1].keys()).removeprefix('dict_keys(').removesuffix(')')
#         d = str(modifiers[2].keys()).removeprefix('dict_keys(').removesuffix(')')
#         id = f'pm{b}wm{c}fm{d}'
#         return id

# def test_model(data, model:CBG):
#     for row in data:
#         model = model.check_closes(row)
#         if (model.get_open_positions() < model.max_positions) and model.buy > row['3. low']:
#             model.buy = min(model.buy, row['2. high'])
#             model.buy_order(row)
#         model = model.Update_Price(row)
#     model = model.closing_time()
#     return model

# def pl(score):
#     log = 1
#     for row in score:
#         match row['type']:
#             case 'Buy':
#                 log *= row['Close']/row['Price']
#             case 'Sell':
#                 log *= 2-(row['Close']/row['Price'])
#     return log

# def get_score(model:CBG):
#     score  = [d for d in model.history if ((d['Outcome'] != 'Ambiguous') & (d['Outcome'] != 'just a baby'))]
#     score = pl(score)
#     score = 10*score
#     return score+(random.random()-0.5)*0.01

# def check_results(model):
#     if not model.history:
#         model = test_model(Gather_Extended('spy'), model)
#     win = len([d for d in model.history if d['Outcome'] == 'Success'])
#     fail = len([d for d in model.history if d['Outcome'] == 'Fail'])
#     babies = len([d for d in model.history if d['Outcome'] == 'just a baby'])
#     age = len([d for d in model.history if d['Outcome'] == 'Too Old'])
#     errors = len(model.history)-win-fail-babies-age
#     return win, fail, babies, age, errors

# def std(score):
#     mean = sum(score)/len(score)
#     stdev = 0
#     for item in score:
#         stdev += (item-mean)**2
#     stdev = (stdev / len(score))**(1/2)
#     return mean, stdev