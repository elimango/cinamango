import c4d

doc = c4d.documents.GetActiveDocument()

def getAllRenderData(op):
    settings = []
    while op:
        settings.append(op.GetName())
        settings += getAllRenderData(op.GetDown())  # Recurse into children
        op = op.GetNext()
    return settings

def getAllMaterials(doc):
    materials = []
    while doc:
        materials.append(doc)
        doc = doc.GetNext()
    return materials

def getAllObjects(doc):
    # recursively collects all objects in the hierarchy starting from op
    objects = []
    while doc:
        objects.append(doc)
        objects += getAllObjects(doc.GetDown())  # Recurse into children
        doc = doc.GetNext()  # Move to next sibling
    return objects

def main(): 
    if doc is None:
        print("No active document.")

    print("\nMaterials:")
    collectmats = getAllMaterials(doc.GetFirstMaterial())    
    for mat in collectmats:
        print(f"  {mat.GetName()}")
    print(f"Found {len(collectmats)}")           

    print("\nObjects:")   
    collectobj = getAllObjects(doc.GetFirstObject())
    for obj in collectobj:
        print(f"  {obj.GetName()}")    
    print(f"Found {len(collectobj)}")   

    print("\nRender Settings:")   
    collectrd = getAllRenderData(doc.GetFirstObject())
    for rd in collectrd:
        print(f"  {rd.GetName()}")    
    print(f"Found {len(collectrd)}")      

    c4d.EventAdd()

if __name__ == '__main__':
    main()