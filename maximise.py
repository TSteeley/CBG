import numpy as np

def discreteDerivative(fun, a:float):
    """# Discrete Derivative
    Takes a function fun and estimates the derivative at the point a.

    Args:
        fun (function): function in the style f(x)
        a (list): Starting position as list i.e. a = [2] or for the
        derivative at mutliple points a list of starting positions i.e. [1,2,3,4]

    Returns:
        list: List of approximated Derivative
    """
    a = np.array(a)
    points = np.matrix([np.add(a,-0.01),a,np.add(a,0.01)], dtype=object)
    vals = np.vectorize(fun)(points.transpose())
    vals = np.diff(vals)
    df = sum(vals.transpose())/(0.01*2)
    df = df.tolist()
    return df[0]

def discreteDoubleDerivative(fun, a):
    a = np.array(a)
    points = np.matrix([np.add(a,-0.01),a,np.add(a,0.01)], dtype=object)
    vals = np.vectorize(fun)(points.transpose())
    vals = np.diff(np.diff(vals))
    df = sum(vals.transpose())/(0.01**2)
    df = df.tolist()
    return df[0]

def discreteGradientVector(fun,a):
    """# Discrete Gradient Vector
    Takes a multivariate function input, with a given starting postion and estimates the
    gradient vector at that point. This is useful for Newton-Raphson style maximisation Function.

    Args:
        fun (function): a multivariate function with list of variables as input, i.e. lambda x: x[0]*x[1]
        a (list(list)): Starting positions need to be put in as [[1,2]] or
        for getting gradients at mutlpile points[[1,1],[1,2]]

    Returns:
        list: Approximated Gradient Vector
    """
    grads = []
    # [[i]*3 for i in a] takes the input list a and makes it 3 lists; [1,2]-> [[1,2],[1,2],[1,2]]
    for j in [[i]*3 for i in a]:
        # Takes this tri list and turns it into a matrix, then makes n of them. One for each variable.
        b = [np.matrix(j)]*len(a[0])
        # Takes these n identical matrices and returns each one the next column is [-0.01;+0;+0.01]
        b = [np.add(i,difMaker(i.shape[1],idx)) for idx, i in enumerate(b)]\
        # Applies the input function
        b = np.vectorize(fun,signature='(n)->()')(b)
        #  takes the difference
        b = [np.diff(i.tolist()) for i in b]
        #  takes the average and makes unit amount
        b = [sum(i)/(0.01*2) for i in b]
        # adds to return function
        grads.append(b)
    return grads

def discreteLaplacian(fun, a):
    grads = []
    # [[i]*3 for i in a] takes the input list a and makes it 3 lists; [1,2]-> [[1,2],[1,2],[1,2]]
    for j in [[i]*3 for i in a]:
        # Takes this tri list and turns it into a matrix, then makes n of them. One for each variable.
        b = [np.matrix(j)]*len(a[0])
        # Takes these n identical matrices and returns each one the next column is [-0.01;+0;+0.01]
        b = [np.add(i,difMaker(i.shape[1],idx)) for idx, i in enumerate(b)]\
        # Applies the input function
        b = np.vectorize(fun,signature='(n)->()')(b)
        #  takes the difference, then again.
        b = [np.diff(i.tolist()) for i in b]
        b = np.diff(b)
        #  takes the average and makes unit amount
        b = [i/(0.01**2) for i in b]
        # adds to return function
        grads.append(b)
    return grads

def difMaker(vars,iteration):
    b = np.zeros([3,vars])
    b[:,iteration] = np.array([-0.01,0,0.01])
    return b

