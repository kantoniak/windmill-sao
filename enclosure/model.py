import FreeCAD as App
import Sketcher


def addRectangle(sketch, x1: float, y1: float, x2: float, y2: float):
  # Corner points
  p_tl = App.Vector(x1, y1, 0)
  p_tr = App.Vector(x2, y1, 0)
  p_br = App.Vector(x2, y2, 0)
  p_bl = App.Vector(x1, y2, 0)

  # Edges
  i1 = sketch.addGeometry(Part.LineSegment(p_tl, p_tr), False)  # top edge
  i2 = sketch.addGeometry(Part.LineSegment(p_tr, p_br), False)  # right edge
  i3 = sketch.addGeometry(Part.LineSegment(p_br, p_bl), False)  # bottom edge
  i4 = sketch.addGeometry(Part.LineSegment(p_bl, p_tl), False)  # left edge

  # Close rectangle: make endpoints coincident
  # Line segment point indices: 1 = start point, 2 = end point
  sketch.addConstraint(Sketcher.Constraint('Coincident', i1, 2, i2, 1))
  sketch.addConstraint(Sketcher.Constraint('Coincident', i2, 2, i3, 1))
  sketch.addConstraint(Sketcher.Constraint('Coincident', i3, 2, i4, 1))
  sketch.addConstraint(Sketcher.Constraint('Coincident', i4, 2, i1, 1))

  # Constrain vertical/horizontal edges
  sketch.addConstraint(Sketcher.Constraint('Horizontal', i1))  # top edge
  sketch.addConstraint(Sketcher.Constraint('Vertical', i2))    # right edge
  sketch.addConstraint(Sketcher.Constraint('Horizontal', i3))  # bottom edge
  sketch.addConstraint(Sketcher.Constraint('Vertical', i4))    # left edge

  return (i1, i2, i3, i4)


doc = App.newDocument("Enclosure")

# Add params
ss = doc.addObject("Spreadsheet::Sheet", "Params")
ss.set("A1", "CUBE_SIDE")
ss.set("B1", "30")
ss.setAlias("B1", "CUBE_SIDE")
doc.recompute()

# Cube
cube = doc.addObject("PartDesign::Body", "Cube")
cube_sketch = cube.newObject("Sketcher::SketchObject", "TopView")
cube_sketch.AttachmentSupport = [(doc.getObject("XY_Plane"), "")]
cube_sketch.MapMode = "FlatFace"

(top_edge, right_edge, bottom_edge, left_edge) = addRectangle(cube_sketch, -1, -1, 1, 1)
cube_sketch.addConstraint(Sketcher.Constraint('Symmetric', 1, 2, 3, 2, -1, 1))
constraint_width = cube_sketch.addConstraint(Sketcher.Constraint('DistanceX', left_edge, 1, right_edge, 2, 1))
constraint_height = cube_sketch.addConstraint(Sketcher.Constraint('DistanceY', top_edge, 2, bottom_edge, 1, 30))
cube_sketch.setExpression(f'Constraints[{constraint_width}]', 'Params.CUBE_SIDE')
cube_sketch.setExpression(f'Constraints[{constraint_height}]', 'Params.CUBE_SIDE')

doc.recompute()

cube_pad = cube.newObject('PartDesign::Pad','Pad')
cube_pad.Profile = (cube_sketch, [''])
cube_pad.setExpression('Length', 'Params.CUBE_SIDE')
doc.recompute()

doc.saveAs("exports/enclosure.FCStd")
