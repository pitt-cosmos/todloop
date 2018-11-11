import numpy as np

class Hist1D(object):

    def __init__(self, xlow, xhigh, nbins):
        self.nbins = nbins
        self.xlow  = xlow
        self.xhigh = xhigh
        self.hist, edges = np.histogram([], bins=nbins, range=(xlow, xhigh))
        self.bins = (edges[:-1] + edges[1:]) / 2.

    def fill(self, value, weight=1):
        hist, edges = np.histogram([value], bins=self.nbins, range=(self.xlow, self.xhigh))
        self.hist += hist*weight

    @property
    def data(self):
        return self.bins, self.hist
        
