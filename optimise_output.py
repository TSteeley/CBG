import scipy.optimize as opt
from Models import *
import pickle
from math import inf
import time
import multiprocessing as mp


def fun(vars: list, tickers: list, model: full_control):
    model = model.update_args(vars)
    for data in tickers:
        model = test_model(data, model)
        model.score.append(get_score(model))
        model.history = []
    mean, stdev = std(model.score)
    model.score = mean-stdev
    results: list = pickle.load(open(f'./active.pkl', 'rb'))
    current: full_control = [i for i in results if i.id == model.id][0]
    if model.score > current.score:
        results.remove(current)
        results.append(model)
        successful = False
        while not successful:
            try:
                save(results)
                successful = True
            except:
                pass
    # print(f'{vars} {model.score}')
    return -model.score


def save(data):
    pickle.dump(data, open('active.pkl', 'wb'))
# tickers = ['spy','qqq','tqqq', 'aapl', 'msft', 'ura', 'xbi', 'arkk', 'slv','lit']


def check_a_model(models: list):
    checked_models = []
    for model in models:
        active: list = pickle.load(open('./active.pkl', 'rb'))
        active.append(model)
        pickle.dump(active, open('active.pkl', 'wb'))
        for _ in range(5):
            # print('New run')
            guess = pickle.load(open('./active.pkl', 'rb'))
            guess = ([i for i in guess if i.id == model.id][0]).args
            limits = bounds(len(guess))
            opt.minimize(fun, x0=guess, args=(pickle.load(
                open('./data.pkl', 'rb')), model), bounds=limits)

        close: list = pickle.load(open(f'./active.pkl', 'rb'))
        best = [i for i in close if i.id == model.id][0]
        checked_models.append(best)
        close.remove(best)
        pickle.dump(close, open('active.pkl', 'wb'))

    if len(checked_models) > 1:
        checked_models.sort(key=lambda a: a.score, reverse=True)
        best = checked_models[0]
        best.id = best.id[:-1]
        check_a_model([best])
    else:
        checked = pickle.load(open('./checked_models.pkl', 'rb'))
        checked.append(best)
        pickle.dump(checked, open('checked_models.pkl', 'wb'))


def main():
    models: list = pickle.load(open('./models_to_assess.pkl', 'rb'))
    try:
        process = models[0:5]
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
    active: list = pickle.load(open('./active.pkl', 'rb'))

    while active:
        mod = active[0]
        if mod.id[-1].isdigit():
            friends = [i for i in active if mod.id[:-1] in i.id[:-1]]
            active = [i for i in active if mod.id[:-1] not in i.id[:-1]]
            models.append(friends)
        else:
            models.append(mod)
            active.remove(mod)

    pickle.dump(active, open('active.pkl', 'wb'))
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


if __name__ == '__main__':
    main()
