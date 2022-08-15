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
    global best
    for model in models:
        best = copy.deepcopy(model)
        current = copy.deepcopy(model)
        for _ in range(1):
            guess = best.args
            limits = bounds(len(guess))
            opt.minimize(fun, x0=guess, args=(current), bounds=limits)

        checked_models.append(best)
        best = 0
    all = pickle.load(open('all.pkl','rb'))
    all.append(checked_models)
    pickle.dump(all, open('all.pkl','wb'))
    if len(checked_models) > 1:
        checked_models.sort(key=lambda a: a.score, reverse=True)
        best = checked_models[0]
        best.id = best.id[:-1]
        check_a_model([best])
    elif checked_models[0].id[-1].isnumeric():
        errors = pickle.load(open('./errors.pkl', 'rb'))
        errors.append(best)
        pickle.dump(errors, open('errors.pkl', 'wb'))
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
    global best
    # scipy minimise returns the value on which it converges not necessarily the best result,
    # so i pass out the best result myself. If this fucntion has two ouputs it'll confuse
    # minimise so instead i have this global which gets updated to the best score and is
    # fed back in as the guess for subsequent runs
    if test.score > best.score:
        best = copy.deepcopy(test)
    # print(f'Current: {guess} {test.score}') # comment these out if you dont want the ouput full.
    print(f'Best: {best.args} {best.score}') # good if you want to monitor progress
    return -test.score


def main():
    models: list = pickle.load(open('./models_to_assess.pkl', 'rb'))
    try:
        process = models[0:6]
    except IndexError:
        process = models

    open_processess = []

    for model in process:
        p = mp.Process(target=check_a_model, args=[model])
        p.start()
        open_processess.append(p)
        models.remove(model)

    pickle.dump(models, open('models_to_assess.pkl', 'wb'))

    for process in open_processess:
        process.join()

    models: list = pickle.load(open('./models_to_assess.pkl', 'rb'))

    pickle.dump(models, open('models_to_assess.pkl', 'wb'))

    if models:
        main()
    else:
        print('Success')
        a = pickle.load(open('./checked_models.pkl', 'rb'))
        a.sort(key=lambda c: c.score, reverse=True)
        b = a[0:10]
        for i in b:
            print(f'Score {round(i.score,3)}; args {i.id}')

# def main():
#     # for testing code with single model
#     test_model = full_control().construct(
#         basis_wf=[0.24265786,  0.03000016],
#         basis_price='midpoint',
#         modifiers=[{
#         'sma 20': -0.1362125,
#         '20,100 gap': 0.6441436,
#         'mp,100 gap': 0.88179404
#     },{},{}])
#     check_a_model([test_model])


if __name__ == '__main__':
    main()