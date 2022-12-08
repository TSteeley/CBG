% matlab minimise function to optimise values

py.testModel.setup();
fun = @(x) -py.testModel.testModel(test, py.list(x));
X0 = [1.05, 0.95, 30];
[vars, funVal] = fminsearch(fun, X0)