from __main__ import qt, ctk
import SimpleITK as sitk
import numpy as np
from FastMarching_threshold_slicer import FastMarching_threshold_slicer



class CT_seg_alg(object):
    def __init__(self, image_sitk, label_sitk, sigma):
        self.image_sitk = image_sitk
        self.label_sitk = label_sitk
        self.sigma = sigma

    def setup(self):
        #############################
        ##Parameters ################
        #############################
        sigma = self.sigma
        thre = 5 #default is 5 (dont change)
        CT_sitk = self.image_sitk
        roi_sitk = self.label_sitk
        seed = (148,306,80)
        seg = sitk.Image(CT_sitk.GetSize(), sitk.sitkUInt8)
        seg.CopyInformation(CT_sitk)
        seg[seed] = 1
        #seg = sitk.BinaryDilate(blurredFLAIR, 3)
        #segFLAIR = sitk.ConnectedThreshold(blurredFLAIR, seedList=[seed], lower=200, upper=1200)
        
        semiauto = sitk.ConfidenceConnected(CT_sitk, seedList=[seed],
                                   numberOfIterations=5,
                                   multiplier=1.5,
                                   initialNeighborhoodRadius=1,
                                   replaceValue=1)
        print('done')
#        segFLAIR = sitk.VotingBinaryHoleFilling(image1=segFLAIR,
#                                                          radius=[5]*3,
#                                                          majorityThreshold=1,
#                                                          backgroundValue=0,
#                                                          foregroundValue=1)
        vectorRadius = (10, 10, 5)
        kernel = sitk.sitkBall
        semiauto = sitk.BinaryMorphologicalClosing(semiauto,
                                            vectorRadius,
                                            kernel)
        CT=sitk.GetArrayFromImage(CT_sitk)
        roi=sitk.GetArrayFromImage(roi_sitk)
        roi=roi>0
        seedpointobj=FastMarching_threshold_slicer()
        seedpoint=seedpointobj.computeCentroid_swap(roi)

        feature_img=sitk.GradientMagnitudeRecursiveGaussian(CT_sitk, sigma=sigma) 
        speed_img = sitk.BoundedReciprocal(feature_img) # This is parameter free unlike the Sigmoid

        fm_filter = sitk.FastMarchingBaseImageFilter()
        fm_filter.SetTrialPoints([seedpoint])
        fm_filter.SetStoppingValue(1000)
        fm_img = fm_filter.Execute(speed_img)

        seg=sitk.Threshold(fm_img,
                            lower=0,
                            upper=fm_filter.GetStoppingValue(),
                            outsideValue=fm_filter.GetStoppingValue()+1)

        x=sitk.GetArrayFromImage(seg)
        p1, p2 = np.percentile(np.unique(x), (0,thre)) # set (0,5) as default

        return semiauto


