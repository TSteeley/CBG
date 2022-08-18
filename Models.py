from logging import error
from operator import mod
import pandas as pd
from math import inf
import random
from numpy import clip
from Gather_data import Gather


class CBG:
    def __init__():
        self = CBG.__new__()
        self.history = []
        self.open = []
        self.buy = 0
        self.max_positions = inf
        self.age_limit = 200
        self.score = -inf
        self.id = ''
        self.target = 0.03
        self.fail = 0.03
        self.basis = 'midpoint'
        self.price_modifiers = {}
        self.w_modifier = {}
        self.f_modifier = {}
        self.var_length = 2+len(self.price_modifiers)+len(self.w_modifier)+len(self.f_modifier)
        self.args = [0.03,0.03]
        self.bounds = CBG.set_bounds(len(self.args))

    def full_control(basis_wf:list, basis_price: str, modifiers: list):
        self = CBG.__init__()
        self.id = CBG.__set_id(modifiers)
        self.target = basis_wf[0]
        self.fail = basis_wf[1]
        self.basis = basis_price
        self.price_modifiers = modifiers[0]
        self.w_modifier = modifiers[1]
        self.f_modifier = modifiers[2]
        self.var_length = 2+len(self.price_modifiers)+len(self.w_modifier)+len(self.f_modifier)

        self.args = basis_wf
        for part in modifiers:
            for item in part:
                self.args.append(part[item])

        return self

    def update_args(self, vars:list):
        self.score = []
        self.args = vars
        self.target = vars[0]
        self.fail = vars[1]
        count = 2

        for part in [self.price_modifiers, self.w_modifier, self.f_modifier]:
            for item in part:
                part[item] = vars[count]
                count+=1

        return self

    def Update_Price(self, data):
        self.buy = data[self.basis]
        modifier = 1
        for key in self.price_modifiers:
            modifier += data[key]*self.price_modifiers[key]

        self.buy *= modifier
        return self

    def buy_order(self, data):
        buy , sell = 1, 1

        for key in self.w_modifier:
            buy += data[key]*self.w_modifier[key]
        for key in self.f_modifier:
            sell+= data[key]*self.f_modifier[key]

        buy = max(1, buy + self.target)
        sell=  clip(sell-self.fail,0,1)

        self.open.append({
            'time': data['time'],
            'age':0,
            'type': 'Buy',
            'Price':self.buy,
            'win': self.buy*buy,
            'fail': self.buy*sell
        })
        return self

    def check_closes(self, data):
        if self.open.__len__() == 0:
            return self

        close = [d for d in self.open if (d['type'] == 'Buy') & ((d['win'] < data['2. high']) | (d['fail'] > data['3. low']) | (d['age'] >= self.age_limit))]

        for row in close:
            if ambiguous(row, data):
                self.history.append({
                    'Open Time': row['time'],
                    'Close Time': data['time'],
                    'type': row['type'],
                    'Price':row['Price'],
                    'Close': 0,
                    'Outcome': 'Ambiguous'
                })
                self.open.remove(row)

            elif win(row, data):
                self.history.append({
                    'Open Time': row['time'],
                    'Close Time': data['time'],
                    'type': row['type'],
                    'Price':row['Price'],
                    'Close': row['win'],
                    'Outcome': 'Success'
                })
                self.open.remove(row)

            elif fail(row, data):
                self.history.append({
                    'Open Time': row['time'],
                    'Close Time': data['time'],
                    'type': row['type'],
                    'Price':row['Price'],
                    'Close': row['fail'],
                    'Outcome': 'Fail'
                })
                self.open.remove(row)

            elif row['age'] >= self.age_limit:
                self.history.append({
                    'Open Time': row['time'],
                    'Close Time': data['time'],
                    'type': row['type'],
                    'Price':row['Price'],
                    'Close': data['4. close'],
                    'Outcome': 'Too Old'
                })
                self.open.remove(row)
        for row in self.open:
            row['age'] += 1
        return self

    def closing_time(self):
        for row in self.open:
            if row['age'] <= self.age_limit:
                self.history.append({
                    'Open Time': row['time'],
                    'Close Time': 'N/A',
                    'type': row['type'],
                    'Price':row['Price'],
                    'Outcome': 'just a baby'
                })
                self.open.remove(row)
            else:
                self.history.append({
                    'Open Time': row['time'],
                    'Close Time': 'N/A',
                    'type': row['type'],
                    'Price':row['Price'],
                    'Outcome': 'remains open'
                })
                self.open.remove(row)
        return self

    def get_open_positions(self):
        return self.open.__len__()

    def get_keys(self):
        keys = []
        for part in [self.price_modifiers, self.w_modifier, self.f_modifier]:
            key = []
            for item in part:
                key.append(item)
            keys.append(keys)
        return keys

    def bounds(self, input):
        if isinstance(input,int):
            bound = [[0.001,inf], [0.02,1]]
            for _ in range(input-2):
                bound.append([-inf,inf])
        elif isinstance(input, list) and len(input) == self.args:
            bound = input
        else:
            if len(input) != self.args:
                error(f'length of bounds {len(input)}, must be equal to length of args {len(self.args)}')
            elif not isinstance(input, int| list):
                error(f'bounds function accepts inputs of type int or type list not type, {type(input)}')
        return bound

    def __set_id(modifiers):
        b = str(modifiers[0].keys()).removeprefix('dict_keys(').removesuffix(')')
        c = str(modifiers[1].keys()).removeprefix('dict_keys(').removesuffix(')')
        d = str(modifiers[2].keys()).removeprefix('dict_keys(').removesuffix(')')
        id = f'pm{b}wm{c}fm{d}'
        return id

def ambiguous(row, data):
    if (row['type'] == 'Buy') and (row['win'] < data['2. high']) and (row['fail'] > data['3. low']):
        return True
    return False

def win(row, data):
    if (row['type'] == 'Buy') and (row['win'] < data['2. high']):
        return True
    return False

def fail(row, data):
    if (row['type'] == 'Buy') and (row['fail'] > data['3. low']):
        return True
    return False

def test_model(data, model:CBG):
    for row in data:
        model = model.check_closes(row)
        if (model.get_open_positions() < model.max_positions) and model.buy > row['3. low']:
            model.buy = min(model.buy, row['2. high'])
            model.buy_order(row)
        model = model.Update_Price(row)
    model = model.closing_time()
    return model

def pl(score):
    log = 1
    for row in score:
        match row['type']:
            case 'Buy':
                log *= row['Close']/row['Price']
            case 'Sell':
                log *= 2-(row['Close']/row['Price'])
    return log

def get_score(model:CBG):
    score  = [d for d in model.history if ((d['Outcome'] != 'Ambiguous') & (d['Outcome'] != 'just a baby'))]
    score = pl(score)
    score = 10*score
    return score+(random.random()-0.5)*0.01

def check_results(model):
    if not model.history:
        model = test_model(Gather_Extended('spy'), model)
    win = len([d for d in model.history if d['Outcome'] == 'Success'])
    fail = len([d for d in model.history if d['Outcome'] == 'Fail'])
    babies = len([d for d in model.history if d['Outcome'] == 'just a baby'])
    age = len([d for d in model.history if d['Outcome'] == 'Too Old'])
    errors = len(model.history)-win-fail-babies-age
    return win, fail, babies, age, errors

def std(score):
    mean = sum(score)/len(score)
    stdev = 0
    for item in score:
        stdev += (item-mean)**2
    stdev = (stdev / len(score))**(1/2)
    return mean, stdev
