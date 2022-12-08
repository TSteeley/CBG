from Models import CBG
from Tech_indicators import *

# Initialise CBG, init attributes which will not change between runs
def setup():
# Initialise, Grab data, interpret
    model = CBG()
    model.set_instruments(('qqq','spy'),intra_indicators=(IHT(),IHTT()), inter_indicators=[rsi(14),my_rsi(14),SMA(50), SMA(200)])
    model.set_buyPrice(lambda x: x['midpoint'])
    return model

# Input
def testModel(model:CBG, args):
    model.set_trigger(lambda x : x[x['rsi 14'] < args[2]])
    model.set_wlCondition(lambda x: x['Buy Price'] * args[0], lambda x: x['Buy Price'] * args[1])

    model.execute_buys()
    model.assess_outcome()
    return model.get_score()