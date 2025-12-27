from helpers import *
from helpers import ConstraintAttachment as CA
import FreeCAD as App
import Sketcher

doc = App.newDocument("Enclosure")
Params = initParams(doc, {
  'CUBE_SIDE': '30'
})

# Cube
cube = doc.addObject("PartDesign::Body", "Cube")
cube_sketch = cube.newObject("Sketcher::SketchObject", "TopView")
cube_sketch.AttachmentSupport = [(doc.getObject("XY_Plane"), "")]
cube_sketch.MapMode = "FlatFace"

(top_edge, right_edge, bottom_edge, left_edge) = addRectangle(cube_sketch, -1, -1, 1, 1)
cube_sketch.addConstraint(Sketcher.Constraint('Symmetric', right_edge, CA.END_POINT, left_edge, CA.END_POINT, -1, 1))
addExpressionConstraint(cube_sketch, 'DistanceX', Params.CUBE_SIDE, left_edge, CA.START_POINT, right_edge, CA.END_POINT)
addExpressionConstraint(cube_sketch, 'DistanceY', Params.CUBE_SIDE, top_edge, CA.END_POINT, bottom_edge, CA.START_POINT)

doc.recompute()

cube_pad = cube.newObject('PartDesign::Pad','Pad')
cube_pad.Profile = (cube_sketch, [''])
cube_pad.setExpression('Length', Params.CUBE_SIDE)
doc.recompute()

doc.saveAs("exports/enclosure.FCStd")
