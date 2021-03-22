import c4d

FRAME = -1

def CalcNormal(a, b, c):
    u = b - a
    v = c - a
    return c4d.Vector(
        (u.y * v.z) - (u.z * v.y),
        (u.z * v.x) - (u.x * v.z),
        (u.x * v.y) - (u.y * v.x),
    ).GetNormalized()

def main():
    global FRAME

    # get hair info
    hairObj = op.GetObject()
    guidesLink = hairObj[c4d.HAIRSTYLE_LINK]
    guidesSegs = hairObj[c4d.HAIRSTYLE_SEGMENTS]
    guidesLen = hairObj[c4d.HAIRSTYLE_LENGTH]

    # only update once per frame
    if doc.GetTime().GetFrame(doc.GetFps()) == FRAME:
        return None

    FRAME = doc.GetTime().GetFrame(doc.GetFps())

    # get mesh info
    res = c4d.utils.SendModelingCommand(
        c4d.MCOMMAND_CURRENTSTATETOOBJECT,
        [guidesLink],
        c4d.MODELINGCOMMANDMODE_ALL,
        c4d.BaseContainer(),
        doc
    )
    obj = res[0]

    points = obj.GetAllPoints()
    polys = obj.GetAllPolygons()
    normals = [c4d.Vector()] * len(points)

    hairObj[c4d.HAIRSTYLE_COUNT] = len(points)

    # make normals
    for poly in polys:
        faceNormal = CalcNormal(points[poly.a], points[poly.b], points[poly.c])
        normals[poly.a] = faceNormal
        normals[poly.b] = faceNormal
        normals[poly.c] = faceNormal
        if not poly.IsTriangle():
            normals[poly.d] = faceNormal

    # Lock hair obj, validate, no flags
    hairObj.Lock(doc, bt, True, 0)

    # Make guides, no validate, 0 flags
    guides = c4d.modules.hair.HairGuides(len(points), guidesSegs)

    # Put guides into hair obj, no clone
    hairObj.SetGuides(guides, False)

    # Set guides world matrix
    guides.SetMg(guidesLink.GetMg())

    # Make guides
    for x in range(len(points)):
        meshPoint = points[x]
        pointNormal = normals[x]
        stepLen = guidesLen / guidesSegs
        for y in range(guidesSegs + 1):
            hairPoint = meshPoint + (pointNormal * (stepLen * y))
            guides.SetPoint((x * (guidesSegs + 1)) + y, hairPoint)

    # Unlock hair obj
    hairObj.Unlock()

    # Update hair obj
    hairObj.Update()