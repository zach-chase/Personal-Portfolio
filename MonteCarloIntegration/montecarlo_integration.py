"""Monte Carlo Integration
<Zach Chase>
"""

from scipy import stats
import numpy as np
from scipy import linalg as la
from matplotlib import pyplot as plt

def ball_volume(n, N=10000):
    """Estimate the volume of the n-dimensional unit ball.

    Parameters:
        n (int): The dimension of the ball. n=2 corresponds to the unit circle,
            n=3 corresponds to the unit sphere, and so on.
        N (int): The number of random points to sample.

    Returns:
        (float): An estimate for the volume of the n-dimensional unit ball.
    """
    
    #Find N random points in n-D Domain
    points = np.random.uniform(-1, 1, (n,N))
    
    #Determin how many are in the ball
    length = la.norm(points, axis=0)
    num_within = np.count_nonzero(length < 1)
    
    #Return an estimate of the volume
    return 2**n*num_within/N
    

def mc_integrate1d(f, a, b, N=10000):
    """Approximate the integral of f on the interval [a,b].

    Parameters:
        f (function): the function to integrate. Accepts and returns scalars.
        a (float): the lower bound of interval of integration.
        b (float): the lower bound of interval of integration.
        N (int): The number of random points to sample.

    Returns:
        (float): An approximation of the integral of f over [a,b].

    Example:
        >>> f = lambda x: x**2
        >>> mc_integrate1d(f, -4, 2)    # Integrate from -4 to 2.
        23.734810301138324              # The true value is 24.
    """
    
    #Find uniform points in range (a,b)
    points = np.random.uniform(a,b,N)
    
    #Imput points into the function
    outputs = f(points)
    
    #Estimate the integral
    return (b-a)*(1/N)*np.sum(outputs)

def mc_integrate(f, mins, maxs, N=10000):
    """Approximate the integral of f over the box defined by mins and maxs.

    Parameters:
        f (function): The function to integrate. Accepts and returns
            1-D NumPy arrays of length n.
        mins (list): the lower bounds of integration.
        maxs (list): the upper bounds of integration.
        N (int): The number of random points to sample.

    Returns:
        (float): An approximation of the integral of f over the domain.

    Example:
        # Define f(x,y) = 3x - 4y + y^2. Inputs are grouped into an array.
        >>> f = lambda x: 3*x[0] - 4*x[1] + x[1]**2

        # Integrate over the box [1,3]x[-2,1].
        >>> mc_integrate(f, [1, -2], [3, 1])
        53.562651072181225              # The true value is 54.
    """
    
    #Convert values to arrays
    max_Values = np.array(maxs)
    min_Values = np.array(mins)
    
    #Determine the sum of points
    points = np.sum(f((np.random.random((max_Values.size, N)).T*(max_Values-min_Values)+min_Values).T))
    
    #Calculate valume
    volume = np.product(max_Values-min_Values)
    
    ##Return approximation of integral
    return volume*points/N

def prob4():
    """Let n=4 and Omega = [-3/2,3/4]x[0,1]x[0,1/2]x[0,1].
    - Define the joint distribution f of n standard normal random variables.
    - Use SciPy to integrate f over Omega.
    - Get 20 integer values of N that are roughly logarithmically spaced from
        10**1 to 10**5. For each value of N, use mc_integrate() to compute
        estimates of the integral of f over Omega with N samples. Compute the
        relative error of estimate.
    - Plot the relative error against the sample size N on a log-log scale.
        Also plot the line 1 / sqrt(N) for comparison.
    """
    
    #Define function
    f = lambda x: (1/(4*np.pi**2)) * np.exp(-(x[0]**2+x[1]**2+x[2]**2+x[3]**2)/2)
    
    #Calculate bounds
    mins = np.array([-3/2, 0, 0, 0])
    maxs = np.array([3/4, 1, 1/2, 1])
    
    #Determine actual integration
    means, cov = np.zeros(4), np.eye(4)
    actual = stats.mvn.mvnun(mins, maxs, means, cov)[0]
    
    #Determine number of samples and convert to int
    values = np.logspace(0, 5, 20).astype(int)
    
    #Find relative error
    estimated = np.array([mc_integrate(f, mins, maxs, N) for N in values])
    error = np.abs(actual-estimated)/np.abs(actual)
    
    #Plot error
    plt.loglog(values, error, label="Function Error")
    plt.loglog(values, 1/np.sqrt(values), label="1/sqrt(N)")
    plt.xlabel("Number of samples")
    plt.ylabel("Relative Error")
    plt.suptitle("Monte Carlo Integration Error")
    plt.legend()
    plt.show()
    return