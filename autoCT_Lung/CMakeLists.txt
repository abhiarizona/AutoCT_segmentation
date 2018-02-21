#----------------------------------------------
set(MODULE_NAME AutoCT_LungSeg)

#----------------------------------------------
set(MODULE_PYTHON_SCRIPTS
    ${MODULE_NAME}.py
    )

set(MODULE_PYTHON_RESOURCES
    ${MODULE_NAME}Wizard/__init__.py
    ${MODULE_NAME}Wizard/CT_seg_alg.py
    ${MODULE_NAME}Wizard/CT_seg_alg_tumor.py	
    ${MODULE_NAME}Wizard/CT_seg_alg_lung.py    
    ${MODULE_NAME}Wizard/FastMarching_threshold_slicer.py
    )

#-----------------------------------------------
slicerMacroBuildScriptedModule(
    NAME ${MODULE_NAME}
    SCRIPTS ${MODULE_PYTHON_SCRIPTS}
    RESOURCES ${MODULE_PYTHON_RESOURCES}
    )
