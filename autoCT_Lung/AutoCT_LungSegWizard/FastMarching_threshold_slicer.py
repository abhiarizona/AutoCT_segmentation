import sys
import SimpleITK as sitk
import numpy as np



class FastMarching_threshold_slicer(object):
    def __init__(self):
        pass


    def computeCentroid_swap(self, I):
        #I is a 3D numpy array representing a binary label map
    
        ## Center of mass code 
        #Created by Yip on 4/14/2016 
        #Assume I is a 3D binary mask  
        i,j,k = I.shape

        #Initialize center of mass
        cmi,cmj,cmk=0,0,0 

        #Total mass of the binary mass
        M = np.float(I.sum())

        cmi=np.dot( range(i), (I.sum(axis=2).sum(axis=1)) )
        cmj=np.dot( range(j), (I.sum(axis=2).sum(axis=0)) )
        cmk=np.dot( range(k), (I.sum(axis=1).sum(axis=0)) )

        #center of mass 
        cmj=int(np.round(cmj/M))
        cmk=int(np.round(cmk/M))
        cmi=int(np.round(cmi/M))
    
        #output = '_'.join( [str(cmi), str(cmj), str(cmk)] ) 
        return (cmk, cmj, cmi) 
