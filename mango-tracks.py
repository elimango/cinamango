import c4d
from c4d import gui

## ANOTHER PROTOTYPING SCRIPT !! IT WILL AND DOES CURRENTLY LOOK LIKE A MESS !! ##

ID_OBJECT_LINK = 1000
ID_PRINT_BUTTON = 1002
FIELDS = 2
doc = c4d.documents.GetActiveDocument()


def SyncTracks(source, target):
    prv = source.GetCTracks()
    nxt = target.GetCTracks()
    nxtNames = []
    prvNames = []
    for name in prv:
        prvNames.append(str(name.GetName()))
    for name in nxt:
        nxtNames.append(str(name.GetName()))
    print("Tracks on Target: \n", nxtNames, "\n")
    print("Tracks on Source: \n", prvNames, "\n")
    for i, sourceTrack in enumerate(prv):
        print("Source Track: {}".format(sourceTrack.GetName()))
        prvCurve = sourceTrack.GetCurve()
        prvCount = prvCurve.GetKeyCount()                
        for j, targetTrack in enumerate(nxt):
            print(" -> Target Track: {}".format(targetTrack.GetName()))
            nxtCurve = targetTrack.GetCurve()
            nxtCount = nxtCurve.GetKeyCount()
            matches = False
            identical = False
            noverlap = False
            if nxtNames[j] not in prvNames:
                noverlap = True            
            if targetTrack.GetName() == sourceTrack.GetName():
                matches = True
                print("Tracks match in both objects!")
            if str(sourceTrack.GetName()) in nxtNames[j] and noverlap:
                print("   - Found identical track in source tracks")
                print("         - Similar in Target: ", 
                        nxtNames[j],
                        "\n         - Similar in Source: ", sourceTrack.GetName())
                identical = True
            if matches or identical:
                print("\nDiffing Source: \n    ",sourceTrack.GetName(),"\nDiffing Target: \n    ",targetTrack.GetName())
                prvkeys = []
                nxtkeys = []
                stashkeys = []
                prvkey = 0
                while prvkey < prvCount:
                    index = prvkeys[prvkey] if len(prvkeys) > 0 and prvkey < len(prvkeys) else prvkey
                    frame = prvCurve.FindNextUnmuted(index)[0].GetTime().GetFrame(doc.GetFps())
                    prvkeys.append(frame)
                    prvkey += 1
                print("Source Track Keys: \n",prvkeys,"\n")
                nxtkey = 0
                while nxtkey < nxtCount:
                    index = nxtkeys[nxtkey] if len(nxtkeys) > 0 and nxtkey < len(nxtkeys) else nxtkey
                    frame = nxtCurve.FindNextUnmuted(index)[0].GetTime().GetFrame(doc.GetFps())
                    nxtkeys.append(frame)
                    nxtkey += 1
                print("Target Track Keys: \n",nxtkeys,"\n")
                for old in nxtkeys:
                    for new in prvkeys:
                        if old == new:
                            nxtkeys.remove(new)
                print("Diffed Keys: \n", nxtkeys,"\n")
                for stashed in sorted(nxtkeys, reverse=True):
                    pre = c4d.BaseTime(stashed, doc.GetFps())
                    found = nxtCurve.FindKey(pre).get("key").GetTime().GetFrame(doc.GetFps()) if nxtCurve.FindKey(pre) else None
                    stashkeys.append(found)
                    nxtCurve.DelKey(stashed, bUndo=True, SynchronizeKeys=True)
                print("Stashed Keys: \n", nxtkeys,"\n")
                for idx, remainder in enumerate(nxtkeys):
                    pre = c4d.BaseTime(stashed, doc.GetFps())
                    index = remainder
                    found, _ = nxtCurve.FindNextUnmuted(index)
                    if found:
                        found.SetInterpolation(nxtCurve, c4d.CINTERPOLATION_STEP)
                        
class ObjectLinkDialog(gui.GeDialog):
    def CreateLayout(self):
        self.SetTitle("Keysync Manager")

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
                SyncTracks(target, source)
        return True

# Open async to allow drag/drop
dlg = ObjectLinkDialog()
dlg.Open(c4d.DLG_TYPE_ASYNC, defaultw=350, defaulth=120)
