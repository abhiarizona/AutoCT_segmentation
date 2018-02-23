from __main__ import qt, ctk
import SimpleITK as sitk
import numpy as np
from FastMarching_threshold_slicer import FastMarching_threshold_slicer



class CT_seg_alg_tumorfine(object):
    def __init__(self, image_sitk, label_sitk, tune):
        self.image_sitk = image_sitk
        self.label_sitk = label_sitk
        self.multiplier = tune

    def setup(self):
        #############################
        ##Parameters ################
        #############################
        #sigma = self.sigma
        thre = 5 #default is 5 (dont change)
        CT_sitk = self.image_sitk
        roi_sitk = self.label_sitk
        multiply = self.multiplier
        CT=sitk.GetArrayFromImage(CT_sitk)
        roi=sitk.GetArrayFromImage(roi_sitk)
        roi=roi>0
        seedpointobj=FastMarching_threshold_slicer()
        seedpoint=seedpointobj.computeCentroid_swap(roi)
#        seed = (172,191,169)
        self.multiplier=multiply +0.025
        semiauto = sitk.ConfidenceConnected(CT_sitk, seedList=[seedpoint],
                                   numberOfIterations=5,
                                   multiplier=multiply+0.025,
                                   initialNeighborhoodRadius=1,
                                   replaceValue=1)
        print('done')
        # Filling holes if any in ROI
        vectorRadius = (10, 10, 5)
        kernel = sitk.sitkBall
        semiauto = sitk.BinaryMorphologicalClosing(semiauto,
                                            vectorRadius,
                                            kernel)
#        b = np.array(semiauto)
#        white_pix = b.reshape(-1)
        nda = sitk.GetArrayFromImage(semiauto)
        white_pix = np.count_nonzero(nda)
#        n_white_pix = np.sum(semiauto == 1)
        print('Number of white pixels:', white_pix) # To check if the tumors  are segmented out well
        if white_pix > 30000:
            return semiauto
        else:
            
            self.multiplier=multiply +0.05
            semiauto = sitk.ConfidenceConnected(CT_sitk, seedList=[seedpoint],
                                                numberOfIterations=5,
                                                multiplier=multiply+0.05,
                                                initialNeighborhoodRadius=1,
                                                replaceValue=1)
            print('done')

            vectorRadius = (10, 10, 5)
            kernel = sitk.sitkBall
            semiauto = sitk.BinaryMorphologicalClosing(semiauto,
                                                       vectorRadius,
                                                       kernel)

            nda = sitk.GetArrayFromImage(semiauto)
            white_pix = np.count_nonzero(nda)

            print('Number of white pixels:', white_pix)
                    
            if white_pix > 30000:
                return semiauto
            else:
                self.multiplier=multiply +0.075
                semiauto = sitk.ConfidenceConnected(CT_sitk, seedList=[seedpoint],
                                                    numberOfIterations=5,
                                                    multiplier=multiply +0.075,
                                                    initialNeighborhoodRadius=1,
                                                    replaceValue=1)
                print('done')

                vectorRadius = (10, 10, 5)
                kernel = sitk.sitkBall
                semiauto = sitk.BinaryMorphologicalClosing(semiauto,
                                                           vectorRadius,
                                                           kernel)

                nda = sitk.GetArrayFromImage(semiauto)
                white_pix = np.count_nonzero(nda)

                print('Number of white pixels:', white_pix)
                if white_pix > 30000:
                            
                    return semiauto
                else:                                                                                    
                    self.multiplier=multiply +0.1
                    semiauto = sitk.ConfidenceConnected(CT_sitk, seedList=[seedpoint],
                                                        numberOfIterations=5,
                                                        multiplier=multiply +0.1,
                                                        initialNeighborhoodRadius=1,
                                                        replaceValue=1)
                    print('done')

                    vectorRadius = (10, 10, 5)
                    kernel = sitk.sitkBall
                    semiauto = sitk.BinaryMorphologicalClosing(semiauto,
                                                               vectorRadius,
                                                               kernel)

                    nda = sitk.GetArrayFromImage(semiauto)
                    white_pix = np.count_nonzero(nda)

                    print('Number of white pixels:', white_pix)
                    # This will work for very small nodules
                    if white_pix > 30000:
                        return semiauto
                    else:                                                                                                                                            
                        self.multiplier=multiply +0.125
                        semiauto = sitk.ConfidenceConnected(CT_sitk, seedList=[seedpoint],
                                                            numberOfIterations=5,
                                                            multiplier=multiply +0.125,
                                                            initialNeighborhoodRadius=1,
                                                            replaceValue=1)
                        print('done')

                        vectorRadius = (10, 10, 5)
                        kernel = sitk.sitkBall
                        semiauto = sitk.BinaryMorphologicalClosing(semiauto,
                                                                   vectorRadius,
                                                                   kernel)

                        nda = sitk.GetArrayFromImage(semiauto)
                        white_pix = np.count_nonzero(nda)

                        print('Number of white pixels:', white_pix)
                        # This will work for very small nodules hopefully (last resort)
                        if white_pix > 30000:
                                    
                            return semiauto
                        else:    
                            self.multiplier=multiply +0.15                                               
                            semiauto = sitk.ConfidenceConnected(CT_sitk, seedList=[seedpoint],
                                                                numberOfIterations=5,
                                                                multiplier=multiply +0.15,
                                                                initialNeighborhoodRadius=1,
                                                                replaceValue=1)
                            print('done')

                            vectorRadius = (10, 10, 5)
                            kernel = sitk.sitkBall
                            semiauto = sitk.BinaryMorphologicalClosing(semiauto,
                                                                       vectorRadius,
                                                                       kernel)

                            nda = sitk.GetArrayFromImage(semiauto)
                            white_pix = np.count_nonzero(nda)

                            print('Number of white pixels:', white_pix)
                            if white_pix > 30000:
                                    
                                return semiauto
                            else:
                            
                                self.multiplier=multiply +0.175                                               
                                semiauto = sitk.ConfidenceConnected(CT_sitk, seedList=[seedpoint],
                                                                    numberOfIterations=5,
                                                                    multiplier=multiply +0.175,
                                                                    initialNeighborhoodRadius=1,
                                                                    replaceValue=1)
                                print('done')

                                vectorRadius = (10, 10, 5)
                                kernel = sitk.sitkBall
                                semiauto = sitk.BinaryMorphologicalClosing(semiauto,
                                                                           vectorRadius,
                                                                           kernel)

                                nda = sitk.GetArrayFromImage(semiauto)
                                white_pix = np.count_nonzero(nda)

                                print('Number of white pixels:', white_pix)
            


        return semiauto



