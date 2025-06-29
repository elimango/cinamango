import c4d
from c4d import gui

ID_OBJECT_LINK = 1000
ID_PRINT_BUTTON = 1002
FIELDS = 2
doc = c4d.documents.GetActiveDocument()
def SyncTracks(source, target):
    prv = source.GetCTracks()
    nxt = target.GetCTracks()
    for sourceTrack in prv:
        prvCurve = sourceTrack.GetCurve()
        prvCount = prvCurve.GetKeyCount()                
        for targetTrack in nxt:
            print("Target Track: {}".format(targetTrack.GetName()))
            nxtCurve = targetTrack.GetCurve()
            nxtCount = nxtCurve.GetKeyCount()
            if targetTrack.GetName() == sourceTrack.GetName():
                prvkeys = []
                nxtkeys = []
                stashkeys = []
                prvkey = 0
                while prvkey < prvCount:
                    index = prvkeys[prvkey] if len(prvkeys) > 0 and prvkey < len(prvkeys) else prvkey
                    frame = prvCurve.FindNextUnmuted(index)[0].GetTime().GetFrame(doc.GetFps())
                    ##matchkey = prvCurve.GetKey(frame)[0].GetTime().GetFrame(doc.GetFps())
                    prvkeys.append(frame)
                    prvkey += 1
                print(prvkeys)
                nxtkey = 0
                while nxtkey < nxtCount:
                    index = nxtkeys[nxtkey] if len(nxtkeys) > 0 and nxtkey < len(nxtkeys) else nxtkey
                    frame = nxtCurve.FindNextUnmuted(index)[0].GetTime().GetFrame(doc.GetFps())
                    ##matchkey = prvCurve.GetKey(frame)[0].GetTime().GetFrame(doc.GetFps())
                    nxtkeys.append(frame)
                    nxtkey += 1
                for old in nxtkeys:
                    for new in prvkeys:
                        if old == new:
                            nxtkeys.remove(new)
                print("Diffed Keys: \n", nxtkeys)
                for stashed in sorted(nxtkeys, reverse=True):
                    pre = c4d.BaseTime(stashed, doc.GetFps())
                    found = nxtCurve.FindKey(pre).get("key").GetTime().GetFrame(doc.GetFps()) if nxtCurve.FindKey(pre) else None
                    stashkeys.append(found)
                    nxtCurve.DelKey(stashed, bUndo=True, SynchronizeKeys=True)
                for frame in stashkeys:
                    if frame in nxtkeys:
                        nxtkeys.remove(frame)
                print("Stashed Keys: \n", nxtkeys)
                for idx, remainder in enumerate(prvkeys):
                    pre = c4d.BaseTime(stashed, doc.GetFps())
                    index = remainder if idx > 0 else idx
                    try:
                        found, _ = nxtCurve.FindNextUnmuted(index)
                        print("Found Key: ", found)
                    except IndexError:
                        found = None
                    if found:
                        found.SetInterpolation(nxtCurve, c4d.CINTERPOLATION_STEP)
                prvkeys.clear()
                nxtkeys.clear()
            else:
                continue

                        
class ObjectLinkDialog(gui.GeDialog):
    def CreateLayout(self):
        self.SetTitle("Key Sync Manager")

        # Begin vertical group with border padding
        self.AddStaticText(1000, c4d.BFH_LEFT, name="Operations")
    
        self.GroupBegin(2000, c4d.BFH_SCALEFIT | c4d.BFV_SCALEFIT, cols=1, rows=0)
        self.GroupBorderSpace(5, 1, 1, 1)  # left, top, right, bottom
        self.GroupBorder(c4d.BORDER_GROUP_IN)
        # Row group: label + link field
        if self.GroupBegin(2001, c4d.BFH_SCALEFIT, cols=2, rows=1):
            bc = c4d.BaseContainer()
            for i in range(FIELDS):
                if i == 0:
                    self.AddStaticText(1000 + i, c4d.BFH_LEFT, name="Source")
                    self.source = self.AddCustomGui(ID_OBJECT_LINK, c4d.CUSTOMGUI_LINKBOX, "", c4d.BFH_SCALEFIT, 0, 0, bc)
                if i == 1:
                    self.AddStaticText(1000 + i, c4d.BFH_LEFT, name="Target")
                    self.target = self.AddCustomGui(ID_OBJECT_LINK, c4d.CUSTOMGUI_LINKBOX, "", c4d.BFH_SCALEFIT, 0, 0, bc)
            # Optional: restrict to polygon objects only
            # bc.SetInt32(c4d.LINKBOX_FILTER, c4d.Opolygon)
        self.GroupEnd()  # End row group

        self.AddButton(ID_PRINT_BUTTON, c4d.BFH_SCALEFIT, name="Sync Tracks")

        self.GroupEnd()  # End outer group
        return True

    def Command(self, id, msg):
        if id == ID_PRINT_BUTTON:
            invalid = False
            if self.target:
                target = self.target.GetLink()
                if target:
                    print("Linked to:", target.GetName())
                else:
                    print("No object linked.")
                    invalid = True                    
            if self.source:
                source = self.source.GetLink()
                if source:
                    print("Linked to:", source.GetName())
                else:
                    print("No object linked.")
                    invalid = True
            if not invalid:
                print("Syncing tracks...")
                SyncTracks(source, target)
        return True

# Open async to allow drag/drop
dlg = ObjectLinkDialog()
dlg.Open(c4d.DLG_TYPE_ASYNC, defaultw=350, defaulth=120)
