from __main__ import vtk, qt, ctk, slicer
import os 
import fnmatch
import glob
import collections
import pdb
import sys
import numpy as np
import SimpleITK as sitk 
import sitkUtils as su 
import sys
from EditorLib import EditUtil
#import CT_seg_alg_tumor
import AutoCT_LungSegWizard


class AutoCT_LungSeg:
    def __init__(self, parent):
        parent.title = "Auto CT Segmentation"
        parent.categories = ["Examples"]
        parent.contributors = ["Stephen Yip, Lingdao Sha and Abhishek Pandey @TEMPUS Wrote this code"]
        parent.helpText = """ Auto CT Tumor segmentation and 3D tumor generation """
        parent.acknowledgementText = ""
        self.parent = parent

class AutoCT_LungSegWidget:
    def __init__(self, parent = None):
        if not parent:
            self.parent = slicer.qMRMLWidget()
            self.parent.setLayout(qt.QVBoxLayout())
            self.parent.setMRMLScene(slicer.mrmlScene)
        else:
            self.parent = parent
        self.layout = self.parent.layout()
        if not parent:
            self.setup()
            self.parent.show()

    def setup(self):
        # Instantiate and connect widgets ...

        # Collapsible button
        autoCTCollapsibleButton = ctk.ctkCollapsibleButton()
        autoCTCollapsibleButton.text = "Collapsible button for CT auto-segmentation"
        self.layout.addWidget(autoCTCollapsibleButton)

        # Layout within the sample collapsible button
        autoCTFormLayout = qt.QFormLayout(autoCTCollapsibleButton)

        #Load CT image button
        loadCTButton = qt.QPushButton("Load CT image and add ROI annotation")
        loadCTButton.toolTip = "Click to load CT image and then annotate tumor location"
        autoCTFormLayout.addWidget(loadCTButton)
        loadCTButton.connect('clicked(bool)', self.onloadCTButtonClicked)
        
        #Number of nodule to operate
#        loadCTnodulelabel = qt.QInputDialog()
#        loadCTnodulelabel.toolTip = "The tumor number to segment"
#        loadCTnodulelabel.getInt(self, "Get integer","Percentage:")
#        autoCTFormLayout.addWidget(loadCTnodulelabel)
#        loadCTnodulelabel.connect('clicked(bool)', self.onloadCTnodulelabelButtonClicked)
#        

        ####Ajust sigma value for CT##########
        #########################################
#        nodulelabel1 = qt.QLabel()
#        nodulelabel1.setText("Enter the nodule number to process")
#        autoCTFormLayout.addWidget(nodulelabel1)
#        noduleSlider1 = qt.QInputDialog()
#        noduleSlider1.toolTip = "Slide to change nodule number"
#        autoCTFormLayout.addWidget(noduleSlider1)
##        noduleSlider1.setMinimum(0.0)
##        noduleSlider1.setMaximum(20)
##        noduleSlider1.setValue(1.0)
##        noduleSlider.setTickPosition(qt.QSlider.TicksBelow)
##        noduleSlider.setTickInterval(1)
#        self.noduleSlider1 = noduleSlider1
        
        nodulelabel = qt.QLabel()
        nodulelabel.setText("Enter the nodule number to segment (1-10)")
        autoCTFormLayout.addWidget(nodulelabel)
        noduleSlider = qt.QSlider(qt.Qt.Horizontal)
        noduleSlider.toolTip = "Slide to change nodule number"
        noduleSlider.setMinimum(0.0)
        noduleSlider.setMaximum(20)
        noduleSlider.setValue(1.0)
        noduleSlider.setTickPosition(qt.QSlider.TicksBelow)
        noduleSlider.setTickInterval(1)
        self.noduleSlider = noduleSlider
        #label for ticks
        nodulevalues = qt.QGridLayout()
        r1 = qt.QLabel("0")
        r2 = qt.QLabel("2")
        r3 = qt.QLabel("4")
        r4 = qt.QLabel("6")
        r5 = qt.QLabel("8")
        nodulevalues.addWidget(noduleSlider, 0,0,1,5)
        nodulevalues.addWidget(r1,1,0,1,1)
        nodulevalues.addWidget(r2,1,1,1,1)
        nodulevalues.addWidget(r3,1,2,1,1)
        nodulevalues.addWidget(r4,1,3,1,1)
        nodulevalues.addWidget(r5,1,4,1,1)
        #Apply the changes
#        noduleApplyButton = qt.QPushButton("Apply")
#        noduleApplyButton.toolTip = "Click to apply new sigma value"
#        nodulevalues.addWidget(noduleApplyButton, 0,5,2,1)
#        noduleApplyButton.connect('clicked(bool)', self.changesApplyButtonClicked)
        autoCTFormLayout.addRow(nodulevalues)
        # Add vertical spacer
        self.layout.addStretch(1)
        

        #########Button for CT segmentation and 3D generation##########
        ###########################################################
        CTSeg3D_tumorButton = qt.QPushButton("CTSeg3D_tumor")
        CTSeg3D_tumorButton.toolTip = "Click to generate auto segmentation and 3D view of tumor"
        autoCTFormLayout.addWidget(CTSeg3D_tumorButton)
        CTSeg3D_tumorButton.connect('clicked(bool)', self.onCTSeg3D_tumorButtonClicked)
        
        ####Ajust multipler value for CT (fine tuning)##########
        #########################################
        
#        CTfinetuneButton = qt.QPushButton("Fine_tuning")
#        CTfinetuneButton.toolTip = "Fine tuning segmentation for better ROI"
#        autoCTFormLayout.addWidget(CTfinetuneButton)
#        CTfinetuneButton.connect('clicked(bool)', self.onCTfinetuneButtonClicked)


        
        ############## Button segment out lung ############
        CTSeg3D_lungButton = qt.QPushButton("CTSeg3D_lung")
        CTSeg3D_lungButton.toolTip = "Click to generate auto segmentation and 3D view of lung"
        autoCTFormLayout.addWidget(CTSeg3D_lungButton)
        CTSeg3D_lungButton.connect('clicked(bool)', self.onCTSeg3D_lungButtonClicked)

        self.image_loaded = False


    def onloadCTButtonClicked(self):
        # widge to load file
        w = qt.QWidget()
        w.resize(320, 240)
        w.setWindowTitle("Select CT Image")
        image_path = qt.QFileDialog.getOpenFileName(w, 'Open File', '/')
        path = str('/'.join(image_path.split('/')[0:-1]))+'/'
        print(path)
        print(image_path)

        if image_path is not None:
            self.image_loaded = True
            print(image_path)

        filetype = ".nrrd"
        self.filetype = filetype
        lm = slicer.app.layoutManager()
        lm.setLayout(slicer.vtkMRMLLayoutNode.SlicerLayoutFourUpView)
        view = lm.threeDWidget(0).threeDView()
        viewNode = view.mrmlViewNode()

        viewNode.SetBackgroundColor((0,0,0))
        viewNode.SetBackgroundColor2((0,0,0))
        viewNode.SetAxisLabelsVisible(0)
        viewNode.SetBoxVisible(0)

        # load image (master volume)
        load, image = slicer.util.loadVolume(image_path, returnNode=True)
        volumesLogic = slicer.modules.volumes.logic()
        label_name = image.GetName()+"-rough-label"
        label = volumesLogic.CreateLabelVolume(slicer.mrmlScene, image, label_name)
        label_path  = str(path+label_name+filetype)
        print(label_path)

        self.view = view
        self.path = path
        self.image_path = image_path
        self.label_path = label_path
        self.image_name = image.GetName()
        self.label_name = label_name
        self.labelpostfix1 = '_tumor_label'
        self.labelpostfix2 = '_lung_label'
        
        selectionNode = slicer.app.applicationLogic().GetSelectionNode()
        selectionNode.SetReferenceActiveLabelVolumeID(label.GetID())
        EditUtil.EditUtil().propagateVolumeSelection()

        # switch to Edit module
        slicer.util.selectModule('Editor')
        slicer.modules.EditorWidget.toolsBox.selectEffect('PaintEffect')

    def auto3DGen(self):
        labelNodeDisplay = self.labelNode.GetDisplayNode()
        labelNodeDisplay.SetAndObserveColorNodeID('vtkMRMLColorTableNodeFileGenericColors.txt')
        self.labelNode.SetAndObserveDisplayNodeID(labelNodeDisplay.GetID())

        tm = slicer.modules.models.mrmlScene().GetNodesByName('Model_1_1')
        for i in tm:
            slicer.modules.models.mrmlScene().RemoveNode(i)

        modelHNode = slicer.mrmlScene.CreateNodeByClass('vtkMRMLModelHierarchyNode')
        modelHNode.SetName('TumorModel')
        modelHNode = slicer.mrmlScene.AddNode(modelHNode)
        parameters = {}
        parameters["InputVolume"] = self.labelNode
        parameters['ModelSceneFile'] = modelHNode.GetID()
        parameters['Smooth'] = 60
        modelmaker = slicer.modules.modelmaker
        slicer.cli.run(modelmaker, None, parameters, wait_for_completion = True)
        self.view.resetFocalPoint()

        # label_sitk = su.PullFromSlicer(self.label_name)
        # labelarray = sitk.GetArrayFromImage(label_sitk)

        # edit_label = sitk.GetImageFromArray(labelarray)
        # edit_label.CopyInformation(label_sitk)

        # ifw = sitk.ImageFileWriter()
        # ifw.SetFileName(self.semi_label_path)
        # ifw.SetUseCompression(True)
        # ifw.Execute(edit_label)

    def onCTSeg3D_tumorButtonClicked(self):
        if self.image_loaded == True:
            node_num = self.noduleSlider.value/2 #default value of sigma
#            node_num1 = self.noduleSlider1.getInt #default value of sigma
            node_num = int(node_num)
            print("nodule number is: ", node_num)
            output_filepath = str(self.path+self.image_name+self.labelpostfix1+"_"+str(node_num)+self.filetype)
            label_sitk = su.PullFromSlicer(self.label_name)
            image_sitk = su.PullFromSlicer(self.image_name)
            print("Image and label array generated.")
            print("output_filepath is: ",output_filepath)
            #self.multiplier = 1
            seg_alg = AutoCT_LungSegWizard.CT_seg_alg_tumor(image_sitk, label_sitk)
            #self.multi = tune
            seg = seg_alg.setup()
            ifw = sitk.ImageFileWriter()
            ifw.SetFileName(output_filepath)
            ifw.SetUseCompression(True)
            ifw.Execute(seg)

            semi_label_path = output_filepath
            semi_label = slicer.util.loadVolume(semi_label_path, properties={'labelmap':True}, returnNode=True)
            self.semi_label_path = semi_label_path

            labelNode = slicer.util.getNode(pattern=self.image_name+self.labelpostfix1+"_"+str(node_num))
            self.labelNode = labelNode
            self.auto3DGen()

#    def onCTfinetuneButtonClicked(self):
#        if self.image_loaded == True:
#            tune = 2
#            node_num = self.noduleSlider.value/2 #default value of sigma
#            print("nodule number is: ", node_num)
#            output_filepath = str(self.path+self.image_name+self.labelpostfix1+"_"+str(node_num)+self.filetype)
#            label_sitk = su.PullFromSlicer(self.label_name)
#            image_sitk = su.PullFromSlicer(self.image_name)
#            print("Image and label array generated.")
#            print("output_filepath is: ",output_filepath)
#
#            seg_alg = AutoCT_LungSegWizard.CT_seg_alg_tumorfine(image_sitk, label_sitk, tune)
#            seg = seg_alg.setup()
#            ifw = sitk.ImageFileWriter()
#            ifw.SetFileName(output_filepath)
#            ifw.SetUseCompression(True)
#            ifw.Execute(seg)
#
#            semi_label_path = output_filepath
#            semi_label = slicer.util.loadVolume(semi_label_path, properties={'labelmap':True}, returnNode=True)
#            self.semi_label_path = semi_label_path
#
#            labelNode = slicer.util.getNode(pattern=self.image_name+self.labelpostfix1+"_"+str(node_num))
#            self.labelNode = labelNode
#            self.auto3DGen()

    def onCTSeg3D_lungButtonClicked(self):
        if self.image_loaded == True:
            #sigma = self.sigmaSlider.value #default value of sigma
            output_filepath = str(self.path+self.image_name+self.labelpostfix2+self.filetype)
            label_sitk = su.PullFromSlicer(self.label_name)
            image_sitk = su.PullFromSlicer(self.image_name)
            print("Image and label array generated.")
            print("output_filepath is: ",output_filepath)

            seg_alg = AutoCT_LungSegWizard.CT_seg_alg_lung(image_sitk, label_sitk)
            seg = seg_alg.setup()
            ifw = sitk.ImageFileWriter()
            ifw.SetFileName(output_filepath)
            ifw.SetUseCompression(True)
            ifw.Execute(seg)

            semi_label_path = output_filepath
            semi_label = slicer.util.loadVolume(semi_label_path, properties={'labelmap':True}, returnNode=True)
            self.semi_label_path = semi_label_path

            labelNode = slicer.util.getNode(pattern=self.image_name+self.labelpostfix2)
            self.labelNode = labelNode
            self.auto3DGen()








