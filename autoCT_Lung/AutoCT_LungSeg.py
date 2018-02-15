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
#from CT_seg_alg import CT_seg_alg
import AutoCT_LungSegWizard


class AutoCT_LungSeg:
	def __init__(self, parent):
		parent.title = "Auto CT Segmentation"
		parent.categories = ["Examples"]
		parent.contributors = ["Stephen Yip and Lingdao Sha @TEMPUS Wrote this code"]
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


		#########Button for CT segmentation and 3D generation##########
		###########################################################
		CTSeg3DButton = qt.QPushButton("CTSeg3D")
		CTSeg3DButton.toolTip = "Click to generate auto segmentation and 3D view"
		autoCTFormLayout.addWidget(CTSeg3DButton)
		CTSeg3DButton.connect('clicked(bool)', self.onCTSeg3DButtonClicked)

		#####Ajust sigma value for CT##########
		##########################################
		sigmalabel = qt.QLabel()
		sigmalabel.setText("Ajust sigma value for better segmentation (1-10)")
		autoCTFormLayout.addWidget(sigmalabel)
		sigmaSlider = qt.QSlider(qt.Qt.Horizontal)
		sigmaSlider.toolTip = "Slie to thange threshold value"
		sigmaSlider.setMinimum(0.0)
		sigmaSlider.setMaximum(20)
		sigmaSlider.setValue(6.0)
		sigmaSlider.setTickPosition(qt.QSlider.TicksBelow)
		sigmaSlider.setTickInterval(1)
		self.sigmaSlider = sigmaSlider
		#label for ticks
		sigmavalues = qt.QGridLayout()
		r1 = qt.QLabel("0")
		r2 = qt.QLabel("2")
		r3 = qt.QLabel("4")
		r4 = qt.QLabel("6")
		r5 = qt.QLabel("8")
		sigmavalues.addWidget(sigmaSlider, 0,0,1,5)
		sigmavalues.addWidget(r1,1,0,1,1)
		sigmavalues.addWidget(r2,1,1,1,1)
		sigmavalues.addWidget(r3,1,2,1,1)
		sigmavalues.addWidget(r4,1,3,1,1)
		sigmavalues.addWidget(r5,1,4,1,1)
		#Apply the changes
		sigmaApplyButton = qt.QPushButton("Apply")
		sigmaApplyButton.toolTip = "Click to apply new sigma value"
		sigmavalues.addWidget(sigmaApplyButton, 0,5,2,1)
		sigmaApplyButton.connect('clicked(bool)', self.changesApplyButtonClicked)
		autoCTFormLayout.addRow(sigmavalues)
		# Add vertical spacer
		self.layout.addStretch(1)
		
		############## Update manual annotation fixation ############
		updateAnnotation = qt.QPushButton("Update annotation")
		updateAnnotation.toolTip = "Click to update annotation"
		autoCTFormLayout.addWidget(updateAnnotation)
		updateAnnotation.connect('clicked(bool)', self.updateAnnotationButtonClicked)

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
		self.labelpostfix = '_fastmarching'
		
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

	def onCTSeg3DButtonClicked(self):
		if self.image_loaded == True:
			sigma = self.sigmaSlider.value #default value of sigma
			output_filepath = str(self.path+self.image_name+self.labelpostfix+self.filetype)
			label_sitk = su.PullFromSlicer(self.label_name)
			image_sitk = su.PullFromSlicer(self.image_name)
			print("Image and label array generated.")
			print("output_filepath is: ",output_filepath)

			seg_alg = AutoCT_LungSegWizard.CT_seg_alg(image_sitk, label_sitk, sigma)
			seg = seg_alg.setup()
			ifw = sitk.ImageFileWriter()
			ifw.SetFileName(output_filepath)
			ifw.SetUseCompression(True)
			ifw.Execute(seg)

			semi_label_path = output_filepath
			semi_label = slicer.util.loadVolume(semi_label_path, properties={'labelmap':True}, returnNode=True)
			self.semi_label_path = semi_label_path

			labelNode = slicer.util.getNode(pattern=self.image_name+self.labelpostfix)
			self.labelNode = labelNode
			self.auto3DGen()

	def changesApplyButtonClicked(self):
		if self.image_loaded == True:
			sigma = self.sigmaSlider.value
			print("sigma value is: ", sigma)
			output_filepath = str(self.path+self.image_name+self.labelpostfix+self.filetype)
			label_sitk = su.PullFromSlicer(self.label_name)
			image_sitk = su.PullFromSlicer(self.image_name)
			print("Image and label array generated.")
			print("output_filepath is: ",output_filepath)

			seg_alg = AutoCT_LungSegWizard.CT_seg_alg(image_sitk, label_sitk, sigma)
			seg = seg_alg.setup()
			ifw = sitk.ImageFileWriter()
			ifw.SetFileName(output_filepath)
			ifw.SetUseCompression(True)
			ifw.Execute(seg)

			semi_label_path = output_filepath
			semi_label = slicer.util.loadVolume(semi_label_path, properties={'labelmap':True}, returnNode=True)
			self.semi_label_path = semi_label_path

			labelNodeOrd = slicer.util.getNodes(pattern=self.image_name+self.labelpostfix+'*', scene=None, useLists=False)
			labelNodelist = list(labelNodeOrd.items())
			labelNodeName = labelNodelist[-1][0]
			print(labelNodeName)
			labelNode = slicer.util.getNode(pattern=labelNodeName)
			self.labelNode = labelNode
			self.auto3DGen()

	def updateAnnotationButtonClicked(self):
		if self.image_loaded == True:
			labelNodeOrd = slicer.util.getNodes(pattern=self.image_name+self.labelpostfix+'*', scene=None, useLists=False)
			labelNodelist = list(labelNodeOrd.items())
			labelNodeName = labelNodelist[-1][0]
			print(labelNodeName)
			labelNode = slicer.util.getNode(pattern=labelNodeName)
			self.labelNode = labelNode
			self.auto3DGen()

			label_sitk = su.PullFromSlicer(labelNodeName)
			labelarray = sitk.GetArrayFromImage(label_sitk)
			edit_label = sitk.GetImageFromArray(labelarray)
			edit_label.CopyInformation(label_sitk)
			ifw = sitk.ImageFileWriter()
			ifw.SetFileName(self.semi_label_path)
			ifw.SetUseCompression(True)
			ifw.Execute(edit_label)








