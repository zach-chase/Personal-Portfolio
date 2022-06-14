# image_segmentation.py
"""Image Segmentation
<Zach Chase>
"""

import numpy as np
from imageio import imread
from matplotlib import pyplot as plt
import scipy.sparse
import scipy.sparse.linalg


def laplacian(A):
    """Compute the Laplacian matrix of the graph G that has adjacency matrix A.

    Parameters:
        A ((N,N) ndarray): The adjacency matrix of an undirected graph G.

    Returns:
        L ((N,N) ndarray): The Laplacian matrix of G.
    """
    #A is the Adjacency Matrix
    #m, n should be equal
    m, n = np.shape(A)
    
    #Initialize D with the same size as A
    D = np.zeros_like(A)
    
    #Find sum of Col of A
    colSum = A.sum(axis = 0)
    
    #Assign diagonal of D to be sum of Columns of A
    for i in range(0, n):
        D[i][i] = colSum[i]
        
    #Assign L
    L = D - A
    
    return L


def connectivity(A, tol=1e-8):
    """Compute the number of connected components in the graph G and its
    algebraic connectivity, given the adjacency matrix A of G.

    Parameters:
        A ((N,N) ndarray): The adjacency matrix of an undirected graph G.
        tol (float): Eigenvalues that are less than this tolerance are
            considered zero.

    Returns:
        (int): The number of connected components in G.
        (float): the algebraic connectivity of G.
    """
    #Define counter
    counter = 0
    
    #Find L and Eigenvalues of L
    L = laplacian(A)
    E_Values = np.linalg.eigvals(L)
    
    #Determine number of connected components
    for x in range(len(E_Values)):
        if E_Values[x] < tol:
            counter += 1
            
    #Counter is number of connected components
    #Sorted(E_Values)[1] is algebraic connectivity
    
    return counter, np.real(sorted(E_Values)[1])


# Helper function
def get_neighbors(index, radius, height, width):
    """Calculate the flattened indices of the pixels that are within the given
    distance of a central pixel, and their distances from the central pixel.

    Parameters:
        index (int): The index of a central pixel in a flattened image array
            with original shape (radius, height).
        radius (float): Radius of the neighborhood around the central pixel.
        height (int): The height of the original image in pixels.
        width (int): The width of the original image in pixels.

    Returns:
        (1-D ndarray): the indices of the pixels that are within the specified
            radius of the central pixel, with respect to the flattened image.
        (1-D ndarray): the euclidean distances from the neighborhood pixels to
            the central pixel.
    """
    # Calculate the original 2-D coordinates of the central pixel.
    row, col = index // width, index % width

    # Get a grid of possible candidates that are close to the central pixel.
    r = int(radius)
    x = np.arange(max(col - r, 0), min(col + r + 1, width))
    y = np.arange(max(row - r, 0), min(row + r + 1, height))
    X, Y = np.meshgrid(x, y)

    # Determine which candidates are within the given radius of the pixel.
    R = np.sqrt(((X - col)**2 + (Y - row)**2))
    mask = R < radius
    return (X[mask] + Y[mask]*width).astype(np.int), R[mask]


class ImageSegmenter:
    """Class for storing and segmenting images."""

    def __init__(self, filename):
        """Read the image file. Store its brightness values as a flat array."""
        
        
        #Initialize
        self.image = imread(filename)
        self.scaled = self.image / 255.
        
        if len(self.image.shape) == 2:
            self.gray = True
            self.brightness = self.scaled
            self.ravel = np.ravel(self.brightness)
        else:
            self.brightness = self.scaled.mean(axis=2)
            self.ravel = np.ravel(self.brightness)
            
        
    def show_original(self):
        """Display the original image."""
        
        #Display if in color
        if len(self.image.shape) == 3:
            plt.imshow(self.scaled)
            
        #If image is gray
        else:
            plt.imshow(self.brightness, cmap="gray")
            plt.axis("off")
            
        
        return

    def adjacency(self, r=5., sigma_B2=.02, sigma_X2=3.):
        """Compute the Adjacency and Degree matrices for the image graph."""
        
        #Check sizes/assign variables
        if len(self.image.shape) == 3:
            m, n, z = self.image.shape
        else:
            m, n = self.image.shape
            
        #Compute A
        A = scipy.sparse.lil_matrix((m*n, m*n))
        
        #Go through algorithm
        for i in range(m*n):
            neighbors, distances = get_neighbors(i, r, m, n)
            w = [np.exp(-1*abs(self.ravel[i] - self.ravel[neighbors[j]]) / sigma_B2-abs(distances[j]) / sigma_X2) for j in range(len(neighbors))]
            A [i, neighbors] = w
            
            
        #Assign D
        D = np.array(A.sum(axis = 0))[0]

        return A.tocsc(), D

    def cut(self, A, D):
        """Compute the boolean mask that segments the image."""
        
        #Check length
        if len(self.image.shape) == 3:
            m, n, z = self.image.shape
        else:
            m, n = self.image.shape
        
        #Comput Laplacian
        lap = scipy.sparse.csgraph.laplacian(A)
        
        #Construct D
        D_12 = scipy.sparse.diags(1/np.sqrt(D))
        
        #Assign X, find mask
        DLD = D_12 @ lap @ D_12
        eigvals, eigvects = scipy.sparse.linalg.eigsh(DLD, which = "SM", k=2)
        X = eigvects[:,1].reshape(m,n)
        mask = X > 0
        
        return mask


    def segment(self, r=5., sigma_B=.02, sigma_X=3.):
        """Display the original image and its segments."""
        
        A, D = self.adjacency(r, sigma_B, sigma_X)
        mask = self.cut(A,D)
        
        #Assign positive and negative
        if len(self.image.shape) == 3:
            mask = np.dstack((mask, mask, mask))
            positive = self.scaled * mask
            negative = self.scaled *~mask
        
        #Begin subplot
        ax1 = plt.subplot(131)
        
        #If gray image
        if len(self.image.shape) != 3:
            
            #Assign negative/positive
            positive = self.brightness * mask
            negative = self.brightness *~mask
            
            #Show original
            ax1.imshow(self.brightness, cmap = "gray")
            plt.axis("off")
            
            #Show positive
            ax2 = plt.subplot(132)
            ax2.imshow(positive, cmap = "gray")
            plt.axis("off")
            
            #Show negative
            ax3 = plt.subplot(133)
            ax3.imshow(negative, cmap = "gray")
            plt.axis("off")
            
        #If in color
        else:
            #Show original
            ax1.imshow(self.scaled)
            plt.axis("off")
            
            #Show positive image
            ax2 = plt.subplot(132)
            ax2.imshow(positive)
            plt.axis("off")
            
            #Show negative image
            ax3 = plt.subplot(133)
            ax3.imshow(negative)
            plt.axis("off")
            
        plt.show()
