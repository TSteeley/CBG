from Models import *

class weighted_indicators(CBG):
    def __init__(self, basis_wf:list, basis_price: str, modifiers: list):
        super().__init__(data= 'training', stage = 'training')
        self.target = basis_wf[0]
        self.fail = basis_wf[1]
        self.basis = basis_price
        self.price_modifiers = modifiers[0]
        self.w_modifier = modifiers[1]
        self.f_modifier = modifiers[2]
        self.var_length = 2+len(self.price_modifiers)+len(self.w_modifier)+len(self.f_modifier)
        self.args = basis_wf
        self.id = CBG.set_id(modifiers)

        for part in modifiers:
            for item in part:
                self.args.append(part[item])

        self.bounds = weighted_indicators.set_bounds(len(self.args))



    def set_bounds(self, input):
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