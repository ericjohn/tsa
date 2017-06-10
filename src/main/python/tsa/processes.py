import numpy as np

import tsa.numpyutils as npu
import tsa.numpychecks as npc

class ItoProcess(object):
    def __init__(self, processdim=1, noisedim=1, drift=None, diffusion=None):
        self.__processdim = processdim
        self.__noisedim = noisedim
        # Note: the brackets around the lambdas below are essential, otherwise the result of the parsing will not be what we need:
        self.__drift = (lambda t, x: npu.rowof(self.__processdim, 0.)) if drift is None else drift
        self.__diffusion = (lambda t, x: npu.matrixof(self.__processdim, self.__noisedim, 0.)) if diffusion is None else diffusion
        
    @property
    def processdim(self):
        return self.__processdim
    
    @property
    def noisedim(self):
        return self.__noisedim
    
    @property
    def drift(self):
        return self.__drift
    
    @property
    def diffusion(self):
        return self.__diffusion
    
    def __str__(self):
        return 'ItoProcess(processdim=%d, noisedim=%d)' % (self.__processdim, self.__noisedim)
    
class MarkovProcess(object):
    def __init__(self, processdim, noisedim):
        self.__processdim = processdim
        self.__noisedim = noisedim
        
    def propagate(self, time, value, timedelta, variatedelta):
        pass
    
class WienerProcess(ItoProcess):
    def __init__(self, mean=None, vol=None):
        if mean is None and vol is None:
            mean = 0.; vol = 1.
            
        self.__mean, self.__vol = None, None
            
        if mean is not None:
            self.__mean = npu.tondim2(mean, ndim1tocol=True, copy=True)
            processdim = npu.nrow(self.__mean)
        if vol is not None:
            self.__vol = npu.tondim2(vol, ndim1tocol=True, copy=True)
            processdim = npu.nrow(self.__vol)
            
        if self.__mean is None: self.__mean = npu.colof(processdim, 0.)
        if self.__vol is None: self.__vol = np.eye(processdim)
            
        npc.checkcol(self.__mean)
        npc.checknrow(self.__mean, processdim)
        npc.checknrow(self.__vol, processdim)
        
        noisedim = npu.ncol(self.__vol)
        
        npu.makeimmutable(self.__mean)
        npu.makeimmutable(self.__vol)
        
        super(WienerProcess, self).__init__(processdim, noisedim, lambda t, x: self.__mean, lambda t, x: self.__vol)
    
    @staticmethod    
    def makevol2d(sd1, sd2, cor):
        return np.array([[sd1, 0.], [cor*sd2, np.sqrt(1. - cor*cor)*sd2]])
    
    @staticmethod
    def makevolfromcov(cov):
        return np.linalg.cholesky(cov)
    
    @staticmethod
    def create2d(mean1, mean2, sd1, sd2, cor):
        return WienerProcess(npu.col(mean1, mean2), WienerProcess.makevol2d(sd1, sd2, cor))
    
    @staticmethod
    def createfromcov(mean, cov):
        return WienerProcess(mean, WienerProcess.makevolfromcov(cov))

    def __str__(self):
        return 'WienerProcess(processdim=%d, noisedim=%d, mean=%s, vol=%s)' % (self.processdim, self.noisedim, str(self.__mean), str(self.__vol))

class OrnsteinUhlenbeckProcess(ItoProcess):
    def __init__(self, transition=None, mean=None, vol=None):
        if transition is None and mean is None and vol is None:
            transition = 1.; mean = 0.; vol = 1.
            
        self.__transition, self.__mean, self.__vol = None, None, None
            
        if transition is not None:
            self.__transition = npu.tondim2(transition, ndim1tocol=True, copy=True)
            processdim = npu.nrow(self.__transition)
        if mean is not None:
            self.__mean = npu.tondim2(mean, ndim1tocol=True, copy=True)
            processdim = npu.nrow(self.__mean)
        if vol is not None:
            self.__vol = npu.tondim2(vol, ndim1tocol=True, copy=True)
            processdim = npu.nrow(self.__vol)
        
        if self.__transition is None: self.__transition = np.eye(processdim)    
        if self.__mean is None: self.__mean = npu.colof(processdim, 0.)
        if self.__vol is None: self.__vol = np.eye(processdim)
        
        npc.checksquare(self.__transition)
        npc.checknrow(self.__transition, processdim)
        npc.checkcol(self.__mean)
        npc.checknrow(self.__mean, processdim)
        npc.checknrow(self.__vol, processdim)
        
        noisedim = npu.ncol(self.__vol)
        
        npu.makeimmutable(self.__transition)
        npu.makeimmutable(self.__mean)
        npu.makeimmutable(self.__vol)
        
        super(OrnsteinUhlenbeckProcess, self).__init__(processdim, noisedim, lambda t, x: -np.dot(self.__transition, x - self.__mean), lambda t, x: self.__vol)
        
    def __str__(self):
        return 'OrnsteinUhlenbeckProcess(processdim=%d, noisedim=%d, transition=%s, mean=%s, vol=%s)' % (self.processdim, self.noisedim, str(self.__transition), str(self.__mean), str(self.__vol))
    