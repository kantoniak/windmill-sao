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
  'TOTAL_HEIGHT': '80 mm',
  'WINDSHAFT_TILT': '13.75 deg',
  'WINDSHAFT_TO_CAP_BASE_VER': '13.75 mm',
  'WINDSHAFT_TO_CAP_BASE_HOR': '14.4 mm',
  'WINDSHAFT_TO_CAP_TOP_VER': '15.4 mm',
  'TOWER_TOP_WIDTH': '36 mm',
  'TOWER_BOTTOM_WIDTH': '56 mm',
})
doc.RecomputesFrozen = True

def createSG90(doc):
  sg90 = doc.addObject("PartDesign::Body", "SG90")
  xy_plane = sg90.Origin.OriginFeatures[3]
  xz_plane = sg90.Origin.OriginFeatures[4]

  sg90_base_s = sg90.newObject("Sketcher::SketchObject", "Base")
  sg90_base_s.AttachmentSupport = xy_plane
  addCenteredRectangle(sg90_base_s, Params.SG90_BASE_WIDTH, Params.SG90_BASE_DEPTH, *ORIGIN)

  sg90_base_pad = sg90.newObject('PartDesign::Pad','Base_Pad')
  sg90_base_pad.Profile = sg90_base_s
  sg90_base_pad.setExpression('Length', Params.SG90_BASE_HEIGHT)

  # Flange
  sg90_flange_s = sg90.newObject("Sketcher::SketchObject", "Flange")
  sg90_flange_s.AttachmentSupport = xy_plane
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
  sg90_flange_s.recompute()

  # Flange: extrude
  sg90_flange_pad = sg90.newObject('PartDesign::Pad','Flange_Pad')
  sg90_flange_pad.Profile = sg90_flange_s
  sg90_flange_pad.setExpression('Length', Params.SG90_FLANGE_THICKNESS)

  # Flange: mirror
  sg90_flange_m = sg90.newObject('PartDesign::Mirrored', 'Flange_Mirror')
  sg90_flange_m.Originals = [sg90_flange_pad]
  sg90_flange_m.MirrorPlane = xz_plane

  # Bushing
  sg90_bushing_s = sg90.newObject("Sketcher::SketchObject", "Bushing")
  sg90_bushing_s.AttachmentSupport = xy_plane
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
  sg90_bushing_pad.Profile = sg90_bushing_s
  sg90_bushing_pad.setExpression('Length', Params.SG90_BUSHING_HEIGHT)

  # Tooth
  sg90_tooth_s = sg90.newObject("Sketcher::SketchObject", "Tooth")
  sg90_tooth_s.AttachmentSupport = xy_plane
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
  sg90_tooth_pad.Profile = sg90_tooth_s
  sg90_tooth_pad.setExpression('Length', f'{Params.SG90_TEETH_HEIGHT}')

  # Tooth: center axis
  # Note to self: FreeCAD 1.1 will move to Part::DatumLine: https://github.com/FreeCAD/FreeCAD/issues/19095
  sg90_tooth_axis = sg90.newObject("PartDesign::Line", "Tooth_Axis")
  sg90_tooth_axis.AttachmentSupport = sg90_tooth_s
  sg90_tooth_axis.MapMode = 'ObjectZ'
  sg90_tooth_axis.recompute()

  # Tooth: polar
  sg90_tooth_polar = sg90.newObject('PartDesign::PolarPattern','Tooth_PolarPattern')
  sg90_tooth_polar.Originals = [sg90_tooth_pad]
  sg90_tooth_polar.Axis = (sg90_tooth_axis, [''])
  sg90_tooth_polar.Angle = 360
  sg90_tooth_polar.setExpression('Occurrences', f'{Params.SG90_TEETH_COUNT}')
  sg90_tooth_polar.Visibility = True

  # FIXME: Why FreeCAD reorders Flange_Mirror to be the last one?
  sg90.Tip = sg90_flange_m
  sg90.recompute()
  return sg90

servo = createSG90(doc)

### Position servo
def toOriginAndRotate(obj, exprX: str | None, exprY: str | None, exprZ: str | None, rotVector, rotDegreeExpr: str | None):
  base_vec = f'vector(0mm; 0mm; 0mm)'
  base_vec = f"vector(({exprX or '0mm'}); ({exprY or '0mm'}); ({exprZ or '0mm'}))"
  rot_val  = f"rotation(vector({rotVector.x}; {rotVector.y}; {rotVector.z}); {rotDegreeExpr or '0 deg'}) * rotation(vector(0; 0; 1), 180 deg) * rotation(vector(0; 1; 0), 180 deg)"
  center_vec = f"vector(-({exprX or '0mm'}); -({exprY or '0mm'}); -({exprZ or '0mm'}))"
  full_expr = f"placement({base_vec}; {rot_val}; {center_vec})"
  obj.setExpression('Placement', full_expr)

toOriginAndRotate(servo,
    exprX = None,
    exprY = f'-{Params.SG90_BASE_DEPTH} / 2 + {Params.SG90_BASE_WIDTH} / 2',
    exprZ = f'-{Params.SG90_BASE_HEIGHT} - {Params.SG90_BUSHING_HEIGHT}',
    rotVector = App.Vector(1, 0, 0),
    rotDegreeExpr = f'-90 deg - {Params.WINDSHAFT_TILT}')

# Supporting global geometry
# Note to self: FreeCAD 1.1 will move to Part::DatumLine: https://github.com/FreeCAD/FreeCAD/issues/19095
windshaft_axis = doc.addObject("PartDesign::Line", "Windshaft_Axis")
windshaft_axis.AttachmentSupport = None
windshaft_axis.MapMode = 'Deactivated'
windshaft_axis.setExpression('Placement.Rotation.Angle', f'90 deg - {Params.WINDSHAFT_TILT}')
windshaft_axis.setExpression('Placement.Rotation.Axis', u'vector(1; 0; 0)')

# Note to self: FreeCAD 1.1 will move to Part::DatumPoint: https://wiki.freecad.org/PartDesign_Point
tower_top_center = doc.addObject("PartDesign::Point", "Tower_Top_Center")
tower_top_center.MapMode = 'Deactivated'
tower_top_center.setExpression('Placement.Base', f'vector(0; {Params.WINDSHAFT_TO_CAP_BASE_VER}; -{Params.WINDSHAFT_TO_CAP_BASE_VER})')

# Note to self: FreeCAD 1.1 will move to Part::DatumPoint: https://wiki.freecad.org/PartDesign_Point
tower_bottom_center = doc.addObject("PartDesign::Point", "Tower_Bottom_Center")
tower_bottom_center.MapMode = 'Deactivated'
tower_bottom_center.setExpression('Placement.Base', f'vector(0; {Params.WINDSHAFT_TO_CAP_BASE_VER}; {Params.WINDSHAFT_TO_CAP_TOP_VER}-{Params.TOTAL_HEIGHT})')

# Note to self: FreeCAD 1.1 will move to Part::DatumLine: https://github.com/FreeCAD/FreeCAD/issues/19095
tower_axis = doc.addObject("PartDesign::Line", "Tower_Axis")
tower_axis.AttachmentSupport = tower_top_center
tower_axis.MapMode = 'ObjectZ'

# Tower
def createTower(doc):
  tower = doc.addObject("PartDesign::Body", "Tower")
  xy_plane = tower.Origin.OriginFeatures[3]
  xz_plane = tower.Origin.OriginFeatures[4]
  yz_plane = tower.Origin.OriginFeatures[5]

  binder_tower_bottom_center = tower.newObject("PartDesign::SubShapeBinder", "Binder_Tower_Bottom_Center")
  binder_tower_bottom_center.Support = tower_bottom_center

  # Create tower curve, as seen from side
  tower_side_s = tower.newObject("Sketcher::SketchObject", "Tower_Side")
  tower_side_s.AttachmentSupport = tower_top_center
  tower_side_s.MapMode = 'ObjectYZ'
  tower_side_s.AttachmentOffset.Rotation.Axis = App.Vector(0, 1, 0)
  tower_side_s.setExpression('AttachmentOffset.Rotation.Angle', f'180 deg')

  side_bottom_point = addExternalGeomIndexed(tower_side_s, binder_tower_bottom_center, 'Vertex1')

  # FIXME: BSpline created programatically is not editable in the UI and it might be a limitation of FreeCAD v1.0 or
  # headless mode. Control points can't be constrained either, as this geometry is not exposed at the moment(?). As a
  # workaround, you can:
  #   1. Select the spline
  #   2. Select "Increase B-Spline degree"
  #   3. Select the spline again
  #   4. Select "Decrease B-Spline degree"
  # This will add GUI handles for editing.
  side_spline_control_point_pos = App.Vector(18, -30, 0)

  (side_spline,) = tower_side_s.addGeometry([
    Part.BSplineCurve(
      [App.Vector(1, 0, 0), side_spline_control_point_pos, App.Vector(2, -1, 0)],
      None, # ?
      None, # ?
      False,
      2, # Degree
      None, # ?
      False)
    ], False)

  addExpressionConstraint(tower_side_s, 'DistanceX', f'{Params.TOWER_TOP_WIDTH}/2', *ORIGIN, side_spline, CA.START_POINT)
  addExpressionConstraint(tower_side_s, 'DistanceX', f'{Params.TOWER_BOTTOM_WIDTH}/2', *ORIGIN, side_spline, CA.END_POINT)

  tower_side_s.addConstraint([
    Sketcher.Constraint('PointOnObject', side_spline, CA.START_POINT, AxisId.X),
    Sketcher.Constraint('Horizontal', side_spline, CA.END_POINT, side_bottom_point, CA.START_POINT),
  ])
  tower_side_s.recompute()

  tower.recompute()
  return tower

tower = createTower(doc)

doc.RecomputesFrozen = False
doc.recompute()
doc.saveAs("exports/enclosure.FCStd")
