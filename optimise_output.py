from Gather_data import *
import scipy.optimize as opt # first one i got to work, plan to add tensor flow option in the future
from Models import *
import pickle
from math import inf
import time
import multiprocessing as mp
import copy
best = 0

# tickers = ['spy','qqq','tqqq', 'aapl', 'msft', 'ura', 'xbi', 'arkk', 'slv','lit']


def check_a_model(models: list):
    checked_models = []
    for model in models:
        global best
        best = copy.deepcopy(model)
        current = copy.deepcopy(model)
        for _ in range(5):
            guess = best.args
            limits = bounds(len(guess))
            opt.minimize(fun, x0=guess, args=(current), bounds=limits)

        checked_models.append(best)

    if len(checked_models) > 1:
        checked_models.sort(key=lambda a: a.score, reverse=True)
        best = checked_models[0]
        best.id = best.id[:-1]
        check_a_model([best])
    else:
        checked = pickle.load(open('./checked_models.pkl', 'rb'))
        checked.append(best)
        pickle.dump(checked, open('checked_models.pkl', 'wb'))

def fun(guess: list, test: full_control):
    test = test.update_args(guess)
    for ticker in get_tickers():
        data = Gather(ticker=ticker)
        test = test_model(data, test)
        test.score.append(get_score(test))
        test.history = [] # clear history between runs; Plan to change this in futurue for better model analysis
    mean, stdev = std(test.score)
    test.score = mean-stdev # The overall score for the run

    # scipy minimise returns the value on which it converges not necessarily the best result,
    # so i pass out the best result myself. If this fucntion has two ouputs it'll confuse
    # minimise so instead i have this global which gets updated to the best score and is
    # fed back in as the guess for subsequent runs
    global best
    if test.score > best.score:
        best = copy.deepcopy(test)
    print(f'Current: {guess} {test.score}')
    print(f'Best: ({best.args} {best.score})')
    return -test.score


# def main():
#     models: list = pickle.load(open('./models_to_assess.pkl', 'rb'))
#     try:
#         process = models[0:5]
#     except IndexError:
#         process = models

#     open_processess = []

#     for model in process:
#         p = mp.Process(target=check_a_model, args=[model])
#         p.start()
#         open_processess.append(p)
#         models.remove(model)

#     pickle.dump(models, open('models_to_assess.pkl', 'wb'))

#     for process in open_processess:
#         process.join()

#     models: list = pickle.load(open('./models_to_assess.pkl', 'rb'))
#     active: list = pickle.load(open('./active.pkl', 'rb'))

#     while active:
#         mod = active[0]
#         if mod.id[-1].isdigit():
#             friends = [i for i in active if mod.id[:-1] in i.id[:-1]]
#             active = [i for i in active if mod.id[:-1] not in i.id[:-1]]
#             models.append(friends)
#         else:
#             models.append(mod)
#             active.remove(mod)

#     pickle.dump(active, open('active.pkl', 'wb'))
#     pickle.dump(models, open('models_to_assess.pkl', 'wb'))

#     if models:
#         main()
#     else:
#         print('Success')
#         a = pickle.load(open('./checked_models.pkl', 'rb'))
#         a.sort(key=lambda c: c.score, reverse=True)
#         b = a[0:10]
#         for i in b:
#             print(f'Score {round(i.score,3)}; args {i.id}')

def main():
    # for testing code with single model
    test_model = full_control().construct(
        basis_wf=[0.22856,0.03000162],
        basis_price='midpoint',
        modifiers=[{
        'sma 20': 0.1763156,
        '20,100 gap': 0.67904503,
        'mp,100 gap': 0.42993023
    },{},{}])
    check_a_model([test_model])


if __name__ == '__main__':
    main()