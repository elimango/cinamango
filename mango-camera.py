import c4d
from c4d import gui

#https://developers.maxon.net/docs/py/2023_2/modules/c4d.documents/BaseDocument/index.html?highlight=executepasses#BaseDocument.ExecutePasses
doc = c4d.documents.GetActiveDocument()
ID_OBJECT_LINK = 1000
ID_STATIC_TEXT = 1001
ID_PRINT_BUTTON = 1002
ID_CHECKBOX = 1003
ID_TARGET_LINK = 1004
ID_SOURCE_GROUP = 1005
ID_TOGGLE_GROUP = 1006

def ParentObjectToCamera(obj, target):
    tag = c4d.BaseTag(c4d.Tcaconstraint)
    obj.InsertTag(tag)
    doc.AddUndo(c4d.UNDOTYPE_NEWOBJ, tag)
    doc.AddUndo(c4d.UNDOTYPE_CHANGE, tag)    
    bc = tag.GetDataInstance()
    ##c4d.CallButton(bc, c4d.ID_CA_CONSTRAINT_TAG_SET_INITIAL_STATE) # SET INITIAL STATE
    tag[c4d.ID_CA_CONSTRAINT_TAG_PARENT] = True
    tag[c4d.ID_CA_CONSTRAINT_TAG_PARENT_RESET] = True
    tag[c4d.ID_CA_CONSTRAINT_TAG_PARENT_FROZEN] = True
    tag[c4d.ID_CA_CONSTRAINT_TAG_PSR_MAINTAIN] = True
    tag[30001] = target  # Target
    doc.AddUndo(c4d.UNDOTYPE_CHANGE, obj)
    doc.AddUndo(c4d.UNDOTYPE_CHANGE, target)

def SetCurrentTime(currentTime, doc):
    doc.SetTime(currentTime)
    doc.ExecutePasses(None, True, True, False, 0)    

def BakeFrames(obj, target):
    minTime = doc[c4d.DOCUMENT_MINTIME]
    maxTime = doc[c4d.DOCUMENT_MAXTIME]
    fps = doc.GetFps()

    if minTime != maxTime:
        ParentObjectToCamera(obj, target)
        currentTime = minTime
        while (currentTime <= maxTime): 
            SetCurrentTime(currentTime, doc)
            doc.AddUndo(c4d.UNDOTYPE_CHANGE, obj)   
            doc.RecordKey(obj, c4d.ID_BASEOBJECT_FROZEN_POSITION, 
                          c4d.BaseTime(currentTime.GetFrame(fps), fps))
            doc.RecordKey(obj, c4d.ID_BASEOBJECT_FROZEN_ROTATION, 
                          c4d.BaseTime(currentTime.GetFrame(fps), fps))                 
            currentTime += c4d.BaseTime(1, fps)
    obj.GetTag(c4d.Tcaconstraint).Remove()    

class ObjectLinkDialog(gui.GeDialog):
    def CreateLayout(self):
        self.SetTitle("Space Switch Manager")
        # Begin vertical group with border padding
        self.AddStaticText(ID_STATIC_TEXT, c4d.BFH_LEFT, name="Operations")
        self.GroupBegin(ID_SOURCE_GROUP, c4d.BFH_SCALEFIT | c4d.BFV_SCALEFIT, cols=1, rows=1)
        self.GroupBorderSpace(5, 1, 1, 1)  # left, top, right, bottom
        self.GroupBorder(c4d.BORDER_GROUP_IN)
        self.GroupBegin(ID_SOURCE_GROUP, c4d.BFH_SCALEFIT, cols=1, rows=1)
        bc = c4d.BaseContainer()                
        self.AddStaticText(ID_STATIC_TEXT, c4d.BFH_LEFT, name="Source")
        self.source = self.AddCustomGui(ID_OBJECT_LINK, c4d.CUSTOMGUI_LINKBOX, "", c4d.BFH_SCALEFIT, 0, 0, bc)
        self.GroupEnd()  # End row group
        self.GroupBegin(ID_TOGGLE_GROUP, c4d.BFH_SCALEFIT, cols=1, rows=1)
        self.GroupBorderSpace(0, 1, 1, 1)  # left, top, right, bottom                
        self.AddStaticText(ID_STATIC_TEXT, c4d.BFH_LEFT, name="Target")
        self.input = self.AddCustomGui(ID_TARGET_LINK, c4d.CUSTOMGUI_LINKBOX, "", c4d.BFH_SCALEFIT, 0, 0, bc)
        self.target = self.input
        self.GroupEnd()
        self.AddCheckbox(ID_CHECKBOX, c4d.BFH_LEFT, initw=1, inith=1, name="Use view as target") 
        self.AddButton(ID_PRINT_BUTTON, c4d.BFH_SCALEFIT, name="Bake To Space")
        return True
    
    def Command(self, id, msg):  
        viewport: c4d.BaseDraw = doc.GetRenderBaseDraw()
        camera: c4d.BaseObject = viewport.GetSceneCamera(doc)        
        if id == ID_CHECKBOX:
            state = self.GetBool(ID_CHECKBOX)
            self.Enable(ID_TOGGLE_GROUP, not state)
            self.target = None if not state else self.target
            self.target = camera
            self.LayoutChanged(ID_TARGET_LINK)
        if id == ID_PRINT_BUTTON:
            invalid = False            
            if not self.GetBool(ID_CHECKBOX):
                target = self.input.GetLink()
            else:
                target = camera
            if self.source:
                source = self.source.GetLink()
                if source:
                    print("Linked to:", source.GetName())
                else:
                    print("No object linked.")
                    invalid = True
            if not invalid:
                BakeFrames(source, target)
        return True

# Open async to allow drag/drop

dlg = ObjectLinkDialog()
dlg.Open(c4d.DLG_TYPE_ASYNC, defaultw=350, defaulth=120)
doc.EndUndo()
c4d.EventAdd()     