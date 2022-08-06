from itertools import *
import pickle
from Models import full_control
from random import random

keys = [
 'standard deviation',
 'iht',
 'ihtt',
 'ave std',
 'sma 100',
 'sma 100 dirv smooth',
 'sma 100 ddirv smooth',
 'sma 20',
 'sma 20 dirv smooth',
 'sma 20 ddirv smooth',
 'rsi',
 'rsi dirv smooth',
 'rsi ddirv smooth',
 '20,100 gap',
 'mp, 20 gap',
 'mp,100 gap',
 ]

# models = []
# checked: list = pickle.load(open('./checked_models.pkl' , 'rb'))
# checked.sort(key=lambda a: a.score, reverse=True)
# top10 = checked[0:10]

# for item in top10:
#     for item1, item2 in combinations_with_replacement(keys, 2):
#         pass



# pickle.dump(models, open('models_to_assess.pkl', 'wb'))
# # pickle.dump([], open('active.pkl', 'wb'))
# pickle.dump([], open('checked_models.pkl', 'wb'))


def init():
    models = []
    # for item in keys:
    #     a = []
    #     for n in range(5):
    #         b = full_control().construct(
    #             basis_wf=[0.03,0.03],
    #             basis_price='midpoint',
    #             modifiers=[{item:(random()-0.5)*0.1*n},{},{}]
    #         )
    #         b.id = f'{b.id}{str(n)}'
    #         a.append(b)
    #     models.append(a)

    for item1, item2, item3 in combinations(keys,3):
        a = []
        for n in range(5):
            b = full_control().construct(
                basis_wf=[0.03,0.03],
                basis_price='midpoint',
                modifiers=[{item1:(random()-0.5)*n*0.1,item2:(random()-0.5)*0.1*n,
                item3:(random()-0.5)*n*0.1},{},{}]
            )
            b.id = f'{b.id}{str(n)}'
            a.append(b)
        models.append(a)

    pickle.dump(models, open('models_to_assess.pkl', 'wb'))
    pickle.dump([], open('active.pkl', 'wb'))
    pickle.dump([], open('checked_models.pkl', 'wb'))


if __name__ == '__main__':
    init()