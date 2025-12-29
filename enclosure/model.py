from helpers import *
from helpers import ConstraintAttachment as CA
import FreeCAD as App
import Sketcher

doc = App.newDocument("Enclosure")
Params = initParams(doc, {
  'SG90_BASE_HEIGHT': '22.5 mm',
  'SG90_BASE_WIDTH': '12.3 mm',
  'SG90_BASE_DEPTH': '22.8 mm',
  'SG90_FLANGE_BASE_OFFSET': '15.7 mm',
  'SG90_FLANGE_DEPTH': '4.7 mm',
  'SG90_FLANGE_THICKNESS': '2.5 mm',
  'SG90_SCREWHOLE_RADIUS': '1 mm',
  'SG90_SCREWHOLE_GAP': '1.3 mm',
  'SG90_SCREWHOLE_DIST': '2.35 mm',
  'SG90_GEAR_FROMTOP': '12.8 mm',
  'SG90_GEAR_RADIUS': '2.5 mm',
  'SG90_BUSHING_HEIGHT': '4 mm',
  'SG90_TOOTH_OUTER': '2.45 mm',
  'SG90_TOOTH_INNER': '2.3 mm',
  'SG90_TOOTH_SCREWHOLE': '2 mm',
  'SG90_TEETH_COUNT': '24',
  'SG90_TEETH_HEIGHT': '3.2 mm',
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
sg90_flange_s.setExpression('AttachmentOffset.Base.y', f'-{Params.SG90_BASE_DEPTH}/2')
sg90_flange_s.MapMode = 'ObjectXY'

(fedge_il, fedge_bl, fedge_l, fedge_t, fedge_r, fedge_br, fedge_ir, farc, farc_side) = sg90_flange_s.addGeometry([
    Part.LineSegment(App.Vector(-1, -9, 0), App.Vector(-1, -10, 0)),
    Part.LineSegment(App.Vector(-1, -10, 0), App.Vector(-3, -10, 0)),
    Part.LineSegment(App.Vector(-3, -10, 0), App.Vector(-3, 0, 0)),
    Part.LineSegment(App.Vector(-3, 0, 0), App.Vector(3, 0, 0)),
    Part.LineSegment(App.Vector(3, 0, 0), App.Vector(3, -10, 0)),
    Part.LineSegment(App.Vector(3, -10, 0), App.Vector(1, -10, 0)),
    Part.LineSegment(App.Vector(1, -10, 0), App.Vector(1, -9, 0)),
    Part.Arc(App.Vector(1, -9, 0), App.Vector(0, -6, 0), App.Vector(-1, -9, 0)),
    Part.Point(App.Vector(1, -6, 0)),
  ], False)

addExpressionConstraint(sg90_flange_s, 'DistanceX', Params.SG90_BASE_WIDTH, fedge_t, CA.START_POINT, fedge_t, CA.END_POINT)
addExpressionConstraint(sg90_flange_s, 'DistanceX', Params.SG90_SCREWHOLE_GAP, fedge_bl, CA.START_POINT, fedge_br, CA.END_POINT)
addExpressionConstraint(sg90_flange_s, 'DistanceX', Params.SG90_SCREWHOLE_RADIUS, farc_side, CA.START_POINT, *ORIGIN)
addExpressionConstraint(sg90_flange_s, 'DistanceY', Params.SG90_FLANGE_DEPTH, fedge_l, CA.START_POINT, *ORIGIN)
addExpressionConstraint(sg90_flange_s, 'DistanceY', f'{Params.SG90_FLANGE_DEPTH} - {Params.SG90_SCREWHOLE_DIST}', farc, CA.CENTER, *ORIGIN)

sg90_flange_s.addConstraint([
  Sketcher.Constraint('Coincident', fedge_il, CA.END_POINT, fedge_bl, CA.START_POINT),
  Sketcher.Constraint('Coincident', fedge_bl, CA.END_POINT, fedge_l, CA.START_POINT),
  Sketcher.Constraint('Coincident', fedge_l, CA.END_POINT, fedge_t, CA.START_POINT),
  Sketcher.Constraint('Coincident', fedge_t, CA.END_POINT, fedge_r, CA.START_POINT),
  Sketcher.Constraint('Coincident', fedge_r, CA.END_POINT, fedge_br, CA.START_POINT),
  Sketcher.Constraint('Coincident', fedge_br, CA.END_POINT, fedge_ir, CA.START_POINT),
  Sketcher.Constraint('Coincident', fedge_ir, CA.END_POINT, farc, CA.START_POINT),
  Sketcher.Constraint('Coincident', fedge_il, CA.START_POINT, farc, CA.END_POINT),
  Sketcher.Constraint('PointOnObject', farc_side, CA.START_POINT, farc),
  Sketcher.Constraint('PointOnObject', farc, CA.CENTER, AxisId.Y),
  Sketcher.Constraint('Vertical', fedge_l),
  Sketcher.Constraint('Vertical', fedge_r),
  Sketcher.Constraint('Vertical', fedge_il),
  Sketcher.Constraint('Vertical', fedge_ir),
  Sketcher.Constraint('Horizontal', fedge_bl),
  Sketcher.Constraint('Horizontal', fedge_t),
  Sketcher.Constraint('Horizontal', fedge_br),
  Sketcher.Constraint('Horizontal', farc_side, CA.START_POINT, farc, CA.CENTER),
  Sketcher.Constraint('Symmetric', fedge_l, CA.END_POINT, fedge_r, CA.START_POINT, *ORIGIN),
  Sketcher.Constraint('Horizontal', fedge_il, CA.START_POINT, fedge_ir, CA.END_POINT),
  Sketcher.Constraint('Horizontal', fedge_il, CA.END_POINT, fedge_ir, CA.START_POINT),
])

# Flange: extrude
sg90_flange_pad = sg90.newObject('PartDesign::Pad','Flange_Pad')
sg90_flange_pad.Profile = (sg90_flange_s, [''])
sg90_flange_pad.setExpression('Length', Params.SG90_FLANGE_THICKNESS)
sg90.recompute()

# Flange: mirror
sg90_flange_m = sg90.newObject('PartDesign::Mirrored', 'Flange_Mirror')
sg90_flange_m.Originals = [sg90_flange_pad,]
sg90_flange_m.MirrorPlane = (doc.getObject("XZ_Plane"), [''])
sg90.recompute()

# Bushing
sg90_bushing_s = sg90.newObject("Sketcher::SketchObject", "Bushing")
sg90_bushing_s.AttachmentSupport = [(doc.getObject("XY_Plane"), "")]
sg90_bushing_s.setExpression('AttachmentOffset.Base.z', Params.SG90_BASE_HEIGHT)
sg90_bushing_s.MapMode = 'ObjectXY'

(bpoint_t, bpoint_r, bpoint_b) = sg90_bushing_s.addGeometry([
  Part.Point(App.Vector(0, 1, 0)),
  Part.Point(App.Vector(1, 0, 0)),
  Part.Point(App.Vector(0, -1, 0))], False)

addExpressionConstraint(sg90_bushing_s, 'DistanceY', f'{Params.SG90_BASE_DEPTH}/2', bpoint_t, 1)
addExpressionConstraint(sg90_bushing_s, 'DistanceY', f'{Params.SG90_BASE_DEPTH}/2 - {Params.SG90_GEAR_FROMTOP} - {Params.SG90_GEAR_RADIUS}', bpoint_b, 1)
addExpressionConstraint(sg90_bushing_s, 'DistanceX', f'{Params.SG90_BASE_WIDTH}/2', bpoint_r, 1)
addExpressionConstraint(sg90_bushing_s, 'DistanceY', f'{Params.SG90_BASE_DEPTH}/2 - {Params.SG90_BASE_WIDTH}/2', bpoint_r, 1)

sg90_bushing_s.addConstraint([
  Sketcher.Constraint('PointOnObject', bpoint_t, CA.START_POINT, AxisId.Y),
  Sketcher.Constraint('PointOnObject', bpoint_b, CA.START_POINT, AxisId.Y),
])
sg90_bushing_s.recompute()

(brect_ta, brect_ba, brect_l, brect_r) = sg90_bushing_s.addGeometry([
  Part.Arc(App.Vector(1, 0, 0), App.Vector(0, 1, 0), App.Vector(-1, 0, 0)),
  Part.Arc(App.Vector(1, 0, 0), App.Vector(0, -1, 0), App.Vector(-1, 0, 0)),
  Part.LineSegment(App.Vector(-1, 0, 0), App.Vector(-1, 1, 0)),
  Part.LineSegment(App.Vector(1, 0, 0), App.Vector(1, 1, 0))], False)

sg90_bushing_s.addConstraint([
  Sketcher.Constraint('PointOnObject', brect_ta, CA.CENTER, AxisId.Y),
  Sketcher.Constraint('PointOnObject', brect_ba, CA.CENTER, AxisId.Y),
  Sketcher.Constraint('Coincident', brect_l, CA.START_POINT, brect_ba, CA.START_POINT),
  Sketcher.Constraint('Coincident', brect_r, CA.START_POINT, brect_ba, CA.END_POINT),
  Sketcher.Constraint('Coincident', brect_l, CA.END_POINT, brect_ta, CA.END_POINT),
  Sketcher.Constraint('Coincident', brect_r, CA.END_POINT, brect_ta, CA.START_POINT),
  Sketcher.Constraint('PointOnObject', bpoint_t, CA.START_POINT, brect_ta),
  Sketcher.Constraint('PointOnObject', bpoint_r, CA.START_POINT, brect_ta),
  Sketcher.Constraint('PointOnObject', bpoint_b, CA.START_POINT, brect_ba),
  Sketcher.Constraint('Vertical', brect_l),
  Sketcher.Constraint('Horizontal', brect_ta, CA.START_POINT, brect_ta, CA.END_POINT),
  Sketcher.Constraint('Horizontal', brect_ba, CA.START_POINT, brect_ba, CA.END_POINT),
])
sg90_bushing_s.recompute()

addExpressionConstraint(sg90_bushing_s, 'DistanceX', f'{Params.SG90_GEAR_RADIUS}*2', brect_ta, CA.END_POINT, brect_ta, CA.START_POINT)
addExpressionConstraint(sg90_bushing_s, 'Radius', f'{Params.SG90_GEAR_RADIUS}', brect_ba)
sg90_bushing_s.recompute()

# Bushing: extrude
sg90_bushing_pad = sg90.newObject('PartDesign::Pad','Bushing_Pad')
sg90_bushing_pad.Profile = (sg90_bushing_s, [''])
sg90_bushing_pad.setExpression('Length', Params.SG90_BUSHING_HEIGHT)
sg90.recompute()

# Tooth
sg90_tooth_s = sg90.newObject("Sketcher::SketchObject", "Tooth")
sg90_tooth_s.AttachmentSupport = [(doc.getObject("XY_Plane"), "")]
sg90_tooth_s.setExpression('AttachmentOffset.Base.y', f'{Params.SG90_BASE_DEPTH}/2 - {Params.SG90_BASE_WIDTH}/2')
sg90_tooth_s.setExpression('AttachmentOffset.Base.z', f'{Params.SG90_BASE_HEIGHT} + {Params.SG90_BUSHING_HEIGHT}')
sg90_tooth_s.MapMode = 'ObjectXY'

(tooth_e, tooth_t, tooth_tr, tooth_br, tooth_b, tooth_arc) = sg90_tooth_s.addGeometry([
  Part.Point(App.Vector(1, 0, 0)),
  Part.LineSegment(App.Vector(0, 1, 0), App.Vector(1, 1, 0)),
  Part.LineSegment(App.Vector(1, 1, 0), App.Vector(1, 0, 0)),
  Part.LineSegment(App.Vector(1, 0, 0), App.Vector(1, -1, 0)),
  Part.LineSegment(App.Vector(1, -1, 0), App.Vector(0, -1, 0)),
  Part.Arc(App.Vector(0, -1, 0), App.Vector(1, 0, 0), App.Vector(0, 1, 0))], False)

addExpressionConstraint(sg90_tooth_s, 'DistanceX', f'{Params.SG90_TOOTH_OUTER}', tooth_e, 1)
addExpressionConstraint(sg90_tooth_s, 'Distance', f'{Params.SG90_TOOTH_INNER}', tooth_t, CA.END_POINT, tooth_arc, CA.CENTER)
addExpressionConstraint(sg90_tooth_s, 'Diameter', f'{Params.SG90_TOOTH_SCREWHOLE}', tooth_arc)
addExpressionConstraint(sg90_tooth_s, 'Angle', f'360 / {Params.SG90_TEETH_COUNT}', tooth_arc)

sg90_tooth_s.addConstraint([
  Sketcher.Constraint('PointOnObject', tooth_e, CA.START_POINT, AxisId.X),
  Sketcher.Constraint('Coincident', tooth_t, CA.END_POINT, tooth_tr, CA.START_POINT),
  Sketcher.Constraint('Coincident', tooth_tr, CA.END_POINT, tooth_e, CA.START_POINT),
  Sketcher.Constraint('Coincident', tooth_br, CA.START_POINT, tooth_e, CA.START_POINT),
  Sketcher.Constraint('Coincident', tooth_br, CA.END_POINT, tooth_b, CA.START_POINT),
  Sketcher.Constraint('Vertical', tooth_t, CA.END_POINT, tooth_b, CA.START_POINT),
  Sketcher.Constraint('Vertical', tooth_t, CA.START_POINT, tooth_b, CA.END_POINT),
  Sketcher.Constraint('Coincident', tooth_arc, CA.START_POINT, tooth_b, CA.END_POINT),
  Sketcher.Constraint('Coincident', tooth_arc, CA.END_POINT, tooth_t, CA.START_POINT),
  Sketcher.Constraint('Coincident', tooth_arc, CA.CENTER, *ORIGIN),
  Sketcher.Constraint('PointOnObject', tooth_arc, CA.CENTER, tooth_t),
  Sketcher.Constraint('PointOnObject', tooth_arc, CA.CENTER, tooth_b),
])
sg90_tooth_s.recompute()

# Tooth: extrude
sg90_tooth_pad = sg90.newObject('PartDesign::Pad','Tooth_Pad')
sg90_tooth_pad.Profile = (sg90_tooth_s, [''])
sg90_tooth_pad.setExpression('Length', f'{Params.SG90_TEETH_HEIGHT}')
sg90.recompute()

# Tooth: center axis
# Note to self: FreeCAD 1.1 will move to Part::DatumLine: https://github.com/FreeCAD/FreeCAD/issues/19095
sg90_tooth_axis = sg90.newObject("PartDesign::Line", "Tooth_Axis")
sg90_tooth_axis.AttachmentSupport = [(sg90_tooth_s, "")]
sg90_tooth_axis.MapMode = 'ObjectZ'
sg90.recompute()

# Tooth: polar
sg90_tooth_polar = sg90.newObject('PartDesign::PolarPattern','Tooth_PolarPattern')
sg90_tooth_polar.Originals = [sg90_tooth_pad,]
sg90_tooth_polar.Axis = (sg90_tooth_axis, [''])
sg90_tooth_polar.Angle = 360
sg90_tooth_polar.setExpression('Occurrences', f'{Params.SG90_TEETH_COUNT}')
sg90_tooth_polar.Visibility = True
sg90.recompute()

sg90.Tip = sg90_tooth_polar

doc.recompute()
doc.saveAs("exports/enclosure.FCStd")
