from helpers import *
from helpers import ConstraintAttachment as CA
import FreeCAD as App
import Sketcher

doc = App.newDocument("Enclosure")
Params = initParams(doc, {
  'CUBE_SIDE': '30',
  'SG90_BASE_HEIGHT': '22.5 mm',
  'SG90_BASE_WIDTH': '12.3 mm',
  'SG90_BASE_DEPTH': '22.8 mm',
  'SG90_FLANGE_BASE_OFFSET': '15.7 mm',
  'SG90_FLANGE_DEPTH': '4.7 mm',
  'SG90_FLANGE_THICKNESS': '2.5 mm',
  'SG90_SCREWHOLE_RADIUS': '1 mm',
  'SG90_SCREWHOLE_GAP': '1.3 mm',
  'SG90_SCREWHOLE_DIST': '2.35 mm',
})

# SG90
sg90 = doc.addObject("PartDesign::Body", "SG90")
sg90_base_s = sg90.newObject("Sketcher::SketchObject", "Base")
sg90_base_s.AttachmentSupport = [(doc.getObject("XY_Plane"), "")]
addCenteredRectangle(sg90_base_s, Params.SG90_BASE_WIDTH, Params.SG90_BASE_DEPTH, *ORIGIN)

sg90_base_pad = sg90.newObject('PartDesign::Pad','Base_Pad')
sg90_base_pad.Profile = (sg90_base_s, [''])
sg90_base_pad.setExpression('Length', Params.SG90_BASE_HEIGHT)
sg90.recompute()

# Flange
sg90_flange_s = sg90.newObject("Sketcher::SketchObject", "Flange")
sg90_flange_s.AttachmentSupport = [(doc.getObject("XY_Plane"), "")]
sg90_flange_s.setExpression('AttachmentOffset.Base.z', Params.SG90_FLANGE_BASE_OFFSET)
sg90_flange_s.MapMode = 'ObjectXY'

# Flange: outer loop
(edge_bl, edge_l, edge_t, edge_r, edge_br) = sg90_flange_s.addGeometry([
    Part.LineSegment(App.Vector(-1, -2, 0), App.Vector(-3, -2, 0)),
    Part.LineSegment(App.Vector(-3, -2, 0), App.Vector(-3, -1, 0)),
    Part.LineSegment(App.Vector(-3, -1, 0), App.Vector(3, -1, 0)),
    Part.LineSegment(App.Vector(3, -1, 0), App.Vector(3, -2, 0)),
    Part.LineSegment(App.Vector(3, -2, 0), App.Vector(1, -2, 0))
  ], False)

sg90_flange_s.addConstraint([
  Sketcher.Constraint('Vertical', edge_l),
  Sketcher.Constraint('Vertical', edge_r),
  Sketcher.Constraint('Horizontal', edge_bl),
  Sketcher.Constraint('Horizontal', edge_br),
  Sketcher.Constraint('Symmetric', edge_l, CA.END_POINT, edge_r, CA.START_POINT, AxisId.Y),
  Sketcher.Constraint('Symmetric', edge_bl, CA.START_POINT, edge_br, CA.END_POINT, AxisId.Y),
  Sketcher.Constraint('Coincident', edge_bl, CA.END_POINT, edge_l, CA.START_POINT),
  Sketcher.Constraint('Coincident', edge_l, CA.END_POINT, edge_t, CA.START_POINT),
  Sketcher.Constraint('Coincident', edge_t, CA.END_POINT, edge_r, CA.START_POINT),
  Sketcher.Constraint('Coincident', edge_r, CA.END_POINT, edge_br, CA.START_POINT)])

addExpressionConstraint(sg90_flange_s, 'DistanceX', Params.SG90_BASE_WIDTH, edge_t, CA.START_POINT, edge_t, CA.END_POINT)
addExpressionConstraint(sg90_flange_s, 'DistanceX', Params.SG90_SCREWHOLE_GAP, edge_bl, CA.START_POINT, edge_br, CA.END_POINT)
addExpressionConstraint(sg90_flange_s, 'DistanceY', f'{Params.SG90_BASE_DEPTH}/2', edge_t, CA.START_POINT, *ORIGIN)
addExpressionConstraint(sg90_flange_s, 'DistanceY', f'{Params.SG90_BASE_DEPTH}/2 + {Params.SG90_FLANGE_DEPTH}', edge_l, CA.START_POINT, *ORIGIN)

# Flange: inner loop
(left, right, arc) = sg90_flange_s.addGeometry([
    Part.LineSegment(App.Vector(-0.5, -16, 0), App.Vector(-0.5, -15.5, 0)),
    Part.LineSegment(App.Vector(0.5, -16, 0), App.Vector(0.5, -15.5, 0)),
    Part.Arc(App.Vector(0.5, -15.5, 0), App.Vector(0, -13, 0), App.Vector(-0.5, -15.5, 0))
  ], False)
print(left, right, arc)

sg90_flange_s.addConstraint([
  Sketcher.Constraint('Vertical', left),
  Sketcher.Constraint('Vertical', right),
  Sketcher.Constraint('Coincident', left, CA.START_POINT, edge_bl, CA.START_POINT),
  Sketcher.Constraint('Coincident', right, CA.START_POINT, edge_br, CA.END_POINT),
  Sketcher.Constraint('Coincident', left, CA.END_POINT, arc, CA.END_POINT),
  Sketcher.Constraint('Coincident', right, CA.END_POINT, arc, CA.START_POINT),
  Sketcher.Constraint('PointOnObject', arc, CA.CENTER, AxisId.Y)])

addExpressionConstraint(sg90_flange_s, 'Radius', Params.SG90_SCREWHOLE_RADIUS, arc)
addExpressionConstraint(sg90_flange_s, 'DistanceY', f'{Params.SG90_BASE_DEPTH}/2 + {Params.SG90_FLANGE_DEPTH} - {Params.SG90_SCREWHOLE_DIST}', arc, CA.CENTER, *ORIGIN)

# Flange: extrude
sg90_flange_pad = sg90.newObject('PartDesign::Pad','Flange_Pad')
sg90_flange_pad.Profile = (sg90_flange_s, [''])
sg90_flange_pad.setExpression('Length', Params.SG90_FLANGE_THICKNESS)

sg90.recompute()

# Flange: mirror
sg90_flange_m = sg90.newObject('PartDesign::Mirrored', 'Flange_Mirror')
sg90_flange_m.Originals = [sg90_flange_pad,]
sg90_flange_m.MirrorPlane = (doc.getObject("XZ_Plane"), [''])

doc.recompute()
doc.saveAs("exports/enclosure.FCStd")
