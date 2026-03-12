# set up TGV
from cil.optimisation.functions import MixedL21Norm, BlockFunction, L2NormSquared, ZeroFunction
from cil.optimisation.operators import BlockOperator, GradientOperator
from cil.optimisation.functions import L2NormSquared, IndicatorBox


def setup_explicit_TV(A, value, data, omega=1, alpha=None):
    '''Function to setup LS + TV problem for use with explicit PDHG

    Parameters
    ----------
    A : ProjectionOperator
        Forward operator.
    data : AcquisitionData
    alpha : float
        Regularisation parameter.
    omega : float, default 1.0
        The constant in front of the data fitting term. Mathematicians like it to be 1/2 but it is 1 by default, 
        i.e. it is ignored if it is 1.

    Returns:
    --------
    K : BlockOperator
    F : BlockFunction

    '''

    f1 = L2NormSquared(b=data)
    if omega != 1:
        f1 = omega * f1
    f2 = MixedL21Norm()
    F = BlockFunction(f1, f2)         

    # Define BlockOperator K
                
    K11 = A
    grad = GradientOperator(K11.domain)
    if alpha is None:
        alpha = value * A.norm()/grad.norm()
    print("alpha = ", alpha)
    K21 = alpha * grad
    
    K = BlockOperator(K11, K21)

    return K, F


