from helpers import *
from helpers import ConstraintAttachment as CA
from itertools import pairwise
from BOPTools import SplitFeatures
from BOPTools.BOPFeatures import BOPFeatures
from CompoundTools import CompoundFilter
import importDXF
import math
import Draft
import FreeCAD as App
import MeshPart, Mesh
import Sketcher

doc = App.newDocument("Enclosure")
Params = initParams(doc, {
  'SG90_BASE_HEIGHT': '24.1 mm',
  'SG90_BASE_WIDTH': '12 mm',
  'SG90_BASE_DEPTH': '23 mm',
  'SG90_FLANGE_BASE_OFFSET': '17 mm',
  'SG90_FLANGE_DEPTH': '4.7 mm',
  'SG90_FLANGE_THICKNESS': '2.55  mm',
  'SG90_SCREWHOLE_RADIUS': '1.35 mm',
  'SG90_SCREWHOLE_GAP': '1.3 mm',
  'SG90_SCREWHOLE_DIST': '2.2 mm',
  'SG90_GEAR_FROMTOP': '11.8 mm',
  'SG90_GEAR_RADIUS': '2.75 mm',
  'SG90_BUSHING_HEIGHT': '4.3 mm',
  'SG90_TOOTH_OUTER': '2.45 mm',
  'SG90_TOOTH_INNER': '2.3 mm',
  'SG90_TOOTH_SCREWHOLE': '1.15 mm',
  'SG90_TEETH_COUNT': '24',
  'SG90_TEETH_HEIGHT': '3.2 mm',
  'PLA_EXPANSION': '0.2 mm',
  'OUTER_WALL_THICKNESS': '2 mm',
  'TOTAL_HEIGHT': '80 mm',
  'WINDSHAFT_TILT': '13.75 deg',
  'WINDSHAFT_TO_CAP_BASE_VER': '13.75 mm',
  'WINDSHAFT_TO_CAP_BASE_HOR': '14.4 mm',
  'WINDSHAFT_TO_CAP_TOP_VER': '15.4 mm',
  'TOWER_TOP_WIDTH': '36 mm',
  'TOWER_BOTTOM_WIDTH': '56 mm',
  'PCB_THICKNESS': '1.6 mm',
  'PCB_OUTLINE_TOLERANCE': '0.2 mm',
  'PCB_SERVO_CLEARANCE': '1 mm',
  'CAP_BASE_DIAM': '35 mm',
  'CAP_BASE_HEIGHT': '1.25 mm',
  'CAP_BEARING_DIAM': '36.5 mm',
  'CAP_BEARING_HEIGHT': '2.75 mm',
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

windshaft_front_plane = doc.addObject("PartDesign::Plane", "Windshaft_Front_Plane")
windshaft_front_plane.AttachmentSupport = windshaft_axis
windshaft_front_plane.MapMode = 'NormalToEdge'
windshaft_front_plane.AttachmentOffset.Base.z = -6

# Note to self: FreeCAD 1.1 will move to Part::DatumPoint: https://wiki.freecad.org/PartDesign_Point
tower_top_center = doc.addObject("PartDesign::Point", "Tower_Top_Center")
tower_top_center.MapMode = 'Deactivated'
tower_top_center.setExpression('Placement.Base', f'vector(0; {Params.WINDSHAFT_TO_CAP_BASE_HOR}; -{Params.WINDSHAFT_TO_CAP_BASE_VER})')

# Note to self: FreeCAD 1.1 will move to Part::DatumPoint: https://wiki.freecad.org/PartDesign_Point
tower_top_back = doc.addObject("PartDesign::Point", "Tower_Top_Back")
tower_top_back.MapMode = 'Deactivated'
tower_top_back.setExpression('Placement.Base', f'vector(0; {Params.WINDSHAFT_TO_CAP_BASE_HOR} + ({Params.TOWER_TOP_WIDTH}/2 * tan(22.5 deg)); -{Params.WINDSHAFT_TO_CAP_BASE_VER})')

# Note to self: FreeCAD 1.1 will move to Part::DatumPoint: https://wiki.freecad.org/PartDesign_Point
tower_bottom_center = doc.addObject("PartDesign::Point", "Tower_Bottom_Center")
tower_bottom_center.MapMode = 'Deactivated'
tower_bottom_center.setExpression('Placement.Base', f'vector(0; {Params.WINDSHAFT_TO_CAP_BASE_HOR}; {Params.WINDSHAFT_TO_CAP_TOP_VER}-{Params.TOTAL_HEIGHT})')

# Note to self: FreeCAD 1.1 will move to Part::DatumLine: https://github.com/FreeCAD/FreeCAD/issues/19095
tower_axis = doc.addObject("PartDesign::Line", "Tower_Axis")
tower_axis.AttachmentSupport = tower_top_center
tower_axis.MapMode = 'ObjectZ'

back_plane = doc.addObject("PartDesign::Plane", "Back_Plane")
back_plane.AttachmentSupport = tower_top_back
back_plane.MapMode = 'ObjectXZ'

# Tower
def createTower(doc):
  tower_sketches = doc.addObject("App::DocumentObjectGroup", "Tower_Sketches")

  binder_tower_bottom_center = tower_sketches.newObject("PartDesign::SubShapeBinder", "Binder_Tower_Bottom_Center")
  binder_tower_bottom_center.Support = tower_bottom_center

  def createBaseXYTowerSketch(name, attachmentSupport, verticalDistanceExpr):
    sketch = tower_sketches.newObject("Sketcher::SketchObject", name)
    sketch.AttachmentSupport = attachmentSupport
    sketch.MapMode = 'ObjectXY'

    (top_circle, top_lines) = addOctagon(sketch)
    top_line_back = sketch.addGeometry(Part.LineSegment(App.Vector(-2, 1), App.Vector(2, 1)))

    sketch.addConstraint(Sketcher.Constraint('Coincident', top_circle, CA.CENTER, *ORIGIN))

    sketch.toggleConstruction(top_lines[5])
    sketch.toggleConstruction(top_lines[6])
    sketch.toggleConstruction(top_lines[7])

    addExpressionConstraint(sketch, 'DistanceY', verticalDistanceExpr, top_lines[2], CA.START_POINT, *ORIGIN)
    return sketch, list(top_lines) + [top_line_back]

  # Create top and bottom view sketches
  (tower_top_s, tower_top_s_lines) = createBaseXYTowerSketch("Tower_Top", tower_top_center, f'{Params.TOWER_TOP_WIDTH}/2')
  tower_top_s.addConstraint([
    Sketcher.Constraint('Horizontal', tower_top_s_lines[-1]),
    Sketcher.Constraint('Coincident', tower_top_s_lines[-1], CA.START_POINT, tower_top_s_lines[0], CA.START_POINT),
    Sketcher.Constraint('Coincident', tower_top_s_lines[-1], CA.END_POINT, tower_top_s_lines[4], CA.END_POINT),
  ])
  tower_top_s.recompute()

  (tower_bottom_s, tower_bottom_s_lines) = createBaseXYTowerSketch("Tower_Bottom", tower_bottom_center, f'{Params.TOWER_BOTTOM_WIDTH}/2')
  tower_bottom_s.toggleConstruction(tower_bottom_s_lines[0])
  tower_bottom_s.toggleConstruction(tower_bottom_s_lines[4])

  tower_bottom_s_lines += list(tower_bottom_s.addGeometry([
    Part.LineSegment(App.Vector(-2, -1), App.Vector(-2, 1)),
    Part.LineSegment(App.Vector(2, -1), App.Vector(2, 1)),
  ]))

  extern_top_backpoint = addExternalGeomIndexed(tower_bottom_s, tower_top_s, 'Vertex1')

  tower_bottom_s.addConstraint([
    Sketcher.Constraint('Horizontal', tower_bottom_s_lines[-3]),
    Sketcher.Constraint('Vertical', tower_bottom_s_lines[-2]),
    Sketcher.Constraint('Vertical', tower_bottom_s_lines[-1]),
    Sketcher.Constraint('PointOnObject', tower_bottom_s_lines[-3], CA.START_POINT, tower_bottom_s_lines[0]),
    Sketcher.Constraint('Horizontal', tower_bottom_s_lines[-3], CA.START_POINT, extern_top_backpoint, CA.START_POINT),
    Sketcher.Constraint('Coincident', tower_bottom_s_lines[-2], CA.START_POINT, tower_bottom_s_lines[0], CA.END_POINT),
    Sketcher.Constraint('Coincident', tower_bottom_s_lines[-1], CA.START_POINT, tower_bottom_s_lines[4], CA.START_POINT),
    Sketcher.Constraint('Coincident', tower_bottom_s_lines[-3], CA.START_POINT, tower_bottom_s_lines[-2], CA.END_POINT),
    Sketcher.Constraint('Coincident', tower_bottom_s_lines[-3], CA.END_POINT, tower_bottom_s_lines[-1], CA.END_POINT),
  ])
  tower_bottom_s.recompute()

  # Create tower curve, as seen from side. Starts at a top side midpoint.
  tower_side_s = tower_sketches.newObject("Sketcher::SketchObject", "Tower_Side")
  tower_side_s.AttachmentSupport = tower_top_center
  tower_side_s.MapMode = 'ObjectYZ'
  tower_side_s.AttachmentOffset.Rotation.Axis = App.Vector(0, 1, 0)
  tower_side_s.setExpression('AttachmentOffset.Rotation.Angle', '180 deg')

  side_bottom_point = addExternalGeomIndexed(tower_side_s, binder_tower_bottom_center, 'Vertex1')

  # FIXME: BSpline created programatically is not editable in the UI and it might be a limitation of FreeCAD v1.0 or
  # headless mode. Control points can't be constrained either, as this geometry is not exposed at the moment(?). As a
  # workaround, you can:
  #   1. Select the spline
  #   2. Select "Increase B-Spline degree"
  #   3. Select the spline again
  #   4. Select "Decrease B-Spline degree"
  # This will add GUI handles for editing.
  TOWER_TOP_TO_SPLINE_CONTROL_POINT = 30
  side_spline_control_point_pos = App.Vector(18, -TOWER_TOP_TO_SPLINE_CONTROL_POINT, 0)

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

  # Create tower curve, as seen from an angle. Starts at the top side endpoint
  tower_angle_s = tower_sketches.newObject("Sketcher::SketchObject", "Tower_Angle")
  tower_angle_s.AttachmentSupport = tower_top_center
  tower_angle_s.MapMode = 'ObjectYZ'
  tower_angle_s.AttachmentOffset.Rotation.Axis = App.Vector(0, 1, 0)
  tower_angle_s.setExpression('AttachmentOffset.Rotation.Angle', f'180 deg + 22.5 deg')

  extern_side_spline = addExternalGeomIndexed(tower_angle_s, tower_side_s, 'Edge1')

  # FIXME: BSpline control points are not availale in FreeCAD v1.0 (see above).
  # Project the start point of spline along X axis
  angle_spline_control_point_pos = App.Vector(
    (36 / 2) / math.cos(math.pi / 8), # (Params.TOWER_TOP_WIDTH / 2) / cos(360 deg / 16)
    -TOWER_TOP_TO_SPLINE_CONTROL_POINT,
    0)

  (angle_spline,) = tower_angle_s.addGeometry([
    Part.BSplineCurve([App.Vector(angle_spline_control_point_pos.x, 0, 0), angle_spline_control_point_pos, App.Vector(2, -1, 0)])], False)

  addExpressionConstraint(tower_angle_s, 'DistanceX', f"-({Params.TOWER_TOP_WIDTH} / 2) / cos(22.5 deg)", angle_spline, CA.START_POINT, *ORIGIN)
  addExpressionConstraint(tower_angle_s, 'DistanceX', f"-({Params.TOWER_BOTTOM_WIDTH} / 2) / cos(22.5 deg)", angle_spline, CA.END_POINT, *ORIGIN)

  tower_angle_s.addConstraint([
    Sketcher.Constraint('PointOnObject', angle_spline, CA.START_POINT, AxisId.X),
    Sketcher.Constraint('Horizontal', angle_spline, CA.END_POINT, extern_side_spline, CA.END_POINT),
  ])
  tower_angle_s.recompute()

  # Create spline clones
  def createRotatedClone(sketch, degrees):
    (sketch_clone,) = tower_sketches.addObject(Draft.make_clone(sketch))
    sketch_clone.Label = f'{sketch.Name}_{degrees}'
    sketch_clone.AttachmentSupport = tower_top_center
    sketch_clone.MapMode = 'ObjectYZ'
    sketch_clone.AttachmentOffset.Rotation.Axis = App.Vector(0, 1, 0)
    sketch_clone.setExpression('AttachmentOffset.Rotation.Angle', f'{degrees} deg')
    return sketch_clone

  tower_side_right_s = createRotatedClone(tower_side_s, 180 + 90)
  tower_side_right_s.AttachmentSupport = tower_top_back

  tower_side_left_s = createRotatedClone(tower_side_s, 180 - 90)
  tower_side_left_s.AttachmentSupport = tower_top_back

  tower_angle_247_5_s = createRotatedClone(tower_angle_s, 180 + 22.5 + 45)
  tower_angle_157_5_s = createRotatedClone(tower_angle_s, 180 - 22.5)
  tower_angle_112_5_s = createRotatedClone(tower_angle_s, 180 - 22.5 - 45)

  tower_sketches.recompute()

  # Create back view sketch (geometry projection)
  tower_back_s = tower_sketches.newObject("Sketcher::SketchObject", 'Tower_Back')
  tower_back_s.AttachmentSupport = tower_top_back
  tower_back_s.MapMode = 'ObjectYZ'
  tower_back_s.AttachmentOffset.Rotation.Axis = App.Vector(0, 1, 0)
  tower_back_s.setExpression('AttachmentOffset.Rotation.Angle', '-90 deg')

  # FIXME: This recompute is needed for spline references (why?)
  doc.RecomputesFrozen = False
  doc.recompute()
  doc.RecomputesFrozen = True

  extern_spline_left = addExternalGeomIndexed(tower_back_s, tower_side_left_s, 'Edge1')
  extern_spline_right = addExternalGeomIndexed(tower_back_s, tower_side_right_s, 'Edge1')

  # FIXME: BSpline control points are not availale in FreeCAD v1.0 (see above).
  back_spline_left_control = App.Vector(
    -side_spline_control_point_pos.x,
    side_spline_control_point_pos.y,
    side_spline_control_point_pos.z)
  (back_spline_left, back_spline_right, back_bottom, back_tl, back_tr, back_top) = tower_back_s.addGeometry([
    Part.BSplineCurve([App.Vector(1, 0, 0), back_spline_left_control, App.Vector(2, -1, 0)]),
    Part.BSplineCurve([App.Vector(-1, 0, 0), side_spline_control_point_pos, App.Vector(-2, -1, 0)]),
    Part.LineSegment(App.Vector(2, -1, 0), App.Vector(-2, -1, 0)),
    Part.LineSegment(App.Vector(-2, -1, 0), App.Vector(-2, 1, 0)),
    Part.LineSegment(App.Vector(2, -1, 0), App.Vector(2, 1, 0)),
    Part.LineSegment(App.Vector(-2, 1, 0), App.Vector(2, 1, 0))], False)

  tower_back_s.addConstraint([
    Sketcher.Constraint('Coincident', back_spline_left, CA.START_POINT, extern_spline_left, CA.START_POINT),
    Sketcher.Constraint('Coincident', back_spline_left, CA.END_POINT, extern_spline_left, CA.END_POINT),
    Sketcher.Constraint('Coincident', back_spline_right, CA.START_POINT, extern_spline_right, CA.START_POINT),
    Sketcher.Constraint('Coincident', back_spline_right, CA.END_POINT, extern_spline_right, CA.END_POINT),
    Sketcher.Constraint('Coincident', back_bottom, CA.START_POINT, extern_spline_left, CA.END_POINT),
    Sketcher.Constraint('Coincident', back_bottom, CA.END_POINT, extern_spline_right, CA.END_POINT),
    Sketcher.Constraint('Coincident', back_tl, CA.START_POINT, extern_spline_left, CA.START_POINT),
    Sketcher.Constraint('Coincident', back_tr, CA.START_POINT, extern_spline_right, CA.START_POINT),
    Sketcher.Constraint('Coincident', back_tl, CA.END_POINT, back_top, CA.START_POINT),
    Sketcher.Constraint('Coincident', back_tr, CA.END_POINT, back_top, CA.END_POINT),
    Sketcher.Constraint('Vertical', back_tl),
    Sketcher.Constraint('Vertical', back_tr),
    Sketcher.Constraint('Horizontal', back_top),
  ])

  addExpressionConstraint(tower_back_s, 'DistanceY', f'{Params.OUTER_WALL_THICKNESS} - {Params.PLA_EXPANSION}', back_tl, CA.START_POINT, back_tl, CA.END_POINT)
  tower_back_s.recompute()

  # Build vertical surfaces
  tower_surfaces = doc.addObject("App::DocumentObjectGroup", "Tower_Surfaces")

  def toSurface(sketch_a, sketch_b):
    surface = tower_surfaces.newObject("Surface::GeomFillSurface", "Surface")
    surface.BoundaryList = [(sketch_a, "Edge1"), (sketch_b, "Edge1")]
    return surface

  surface_sketches = [
    tower_side_right_s,
    tower_angle_247_5_s,
    tower_angle_s,
    tower_angle_157_5_s,
    tower_angle_112_5_s,
    tower_side_left_s,
    tower_side_right_s, # Add first face again to add back surface
  ]
  surfaces = [toSurface(a, b) for a, b in pairwise(surface_sketches)]

  def toSurfaceFromSketchEdges(sketch):
    sketch.recompute()
    edge_count = len(sketch.Shape.Edges)
    surface = tower_surfaces.newObject("Surface::Filling", "Surface")
    surface.BoundaryEdges = [(sketch, f"Edge{i}") for i in range(1, edge_count+1)]
    return surface

  surfaces.append(toSurfaceFromSketchEdges(tower_top_s))
  surfaces.append(toSurfaceFromSketchEdges(tower_bottom_s))

  # Create tower solid

  # FIXME: Surfaces don't have Faces if the doc is not recomputed. It looks like surfaces from a single sketch can
  # actually recompute themselved. How to skip this recompute?
  doc.RecomputesFrozen = False
  doc.recompute()
  doc.RecomputesFrozen = True

  solid_obj = doc.addObject("Part::Feature", "Tower_Solid")
  solid_obj.Shape = Part.makeSolid(Part.makeShell([s.Shape.Faces[0] for s in surfaces]))

  # Create tower base (not source accurate, just for visual finish at the bottom)
  tower_base = doc.addObject("PartDesign::Body", "Tower_Base")

  binder_tower_bottom_s = tower_base.newObject("PartDesign::ShapeBinder", f"Binder_{tower_bottom_s.Label}")
  binder_tower_bottom_s.Support = tower_bottom_s

  tower_base_pad = tower_base.newObject("PartDesign::Pad", "Tower_Base_Pad")
  tower_base_pad.Profile = binder_tower_bottom_s
  tower_base_pad.Length = 4

  tower_fuse = doc.addObject("Part::MultiFuse", "Tower_Fuse")
  tower_fuse.Shapes = [solid_obj, tower_base]

  # Cut the towers backside
  tower_back_offset = doc.addObject("Part::Offset2D", "Tower_Back_Offset")
  tower_back_offset.Source = tower_back_s
  tower_back_offset.setExpression("Value", f'-({Params.OUTER_WALL_THICKNESS}) + {Params.PLA_EXPANSION}')

  tower_back_offset_pad = doc.addObject("PartDesign::Pad", "Tower_Back_Offset_Pad")
  tower_back_offset_pad.Profile = tower_back_offset
  tower_back_offset_pad.Reversed = True
  tower_back_offset_pad.setExpression('Length', f'{Params.PCB_THICKNESS} + {Params.PLA_EXPANSION}')

  tower_back_cut = doc.addObject("Part::Cut", "Tower_Back_Cut")
  tower_back_cut.Base = tower_fuse
  tower_back_cut.Tool = tower_back_offset_pad

  # Sketch the servo access tunnel
  tower_tunnelb_s = tower_sketches.newObject("Sketcher::SketchObject", "Tower_Tunnel_Backwards")
  tower_tunnelb_s.AttachmentSupport = windshaft_axis
  tower_tunnelb_s.MapMode = 'ObjectXY'
  tower_tunnelb_s.setExpression('AttachmentOffset.Base.y', f'-{Params.SG90_BASE_HEIGHT}/2 + ({Params.SG90_BASE_WIDTH}/2)')
  tower_tunnelb_s.setExpression('AttachmentOffset.Base.z',
    f'-{Params.SG90_BUSHING_HEIGHT} - {Params.SG90_BASE_HEIGHT} + {Params.SG90_FLANGE_BASE_OFFSET} ' +
    f'+ {Params.SG90_FLANGE_THICKNESS} + {Params.PLA_EXPANSION}')

  addCenteredRectangle(tower_tunnelb_s,
    f'{Params.SG90_BASE_WIDTH} + {Params.PLA_EXPANSION}',
    f'{Params.SG90_BASE_DEPTH} + 2*{Params.SG90_FLANGE_DEPTH} + {Params.PLA_EXPANSION}',
    *ORIGIN)
  tower_tunnelb_s.recompute()

  # Create PCB object
  pcb_offset = doc.addObject("Part::Offset2D", "PCB_Offset")
  pcb_offset.Source = tower_back_s
  pcb_offset.setExpression("Value", f'-({Params.OUTER_WALL_THICKNESS} + {Params.PCB_OUTLINE_TOLERANCE})')

  pcb_base = doc.addObject("PartDesign::Body", "PCB_Base")
  binder_pcb_offset = pcb_base.newObject("PartDesign::ShapeBinder", f"Binder_{pcb_offset.Label}")
  binder_pcb_offset.Support = pcb_offset

  pcb_pad = pcb_base.newObject("PartDesign::Pad", "PCB_Pad")
  pcb_pad.Profile = binder_pcb_offset
  pcb_pad.Reversed = True
  pcb_pad.setExpression('Length', f'{Params.PCB_THICKNESS}')

  binder_pcb_tunnel_container = pcb_base.newObject("PartDesign::ShapeBinder", f"Binder_{tower_tunnelb_s.Name}")
  binder_pcb_tunnel_container.Support = tower_tunnelb_s

  pcb_pocket = pcb_base.newObject("PartDesign::Pocket", "PCB_Pocket")
  pcb_pocket.Profile = binder_pcb_tunnel_container
  pcb_pocket.Type = 1
  pcb_pocket.Reversed = True

  # FIXME: Required for pocket, can we skip this?
  doc.RecomputesFrozen = False
  doc.recompute()
  doc.RecomputesFrozen = True

  pcb_details_s = pcb_base.newObject("Sketcher::SketchObject", "PCB_Details")
  pcb_details_s.AttachmentSupport = tower_top_back
  pcb_details_s.MapMode = 'ObjectXZ'
  pcb_details_s.setExpression('AttachmentOffset.Rotation.Angle', '180 deg')
  pcb_details_s.setExpression('AttachmentOffset.Rotation.Axis', u'vector(0; 1; 0)')

  # FIXME: Is there a better way of determining those points?
  extern_pocket_left = addExternalGeomIndexed(pcb_details_s, pcb_pocket, 'Vertex11')
  extern_pocket_right = addExternalGeomIndexed(pcb_details_s, pcb_pocket, 'Vertex12')

  (detail_l, detail_t, detail_r, detail_br, detail_b, detail_bl) = pcb_details_s.addGeometry([
      Part.LineSegment(App.Vector(-2, -1), App.Vector(-2, 0)),
      Part.LineSegment(App.Vector(-2, 0), App.Vector(2, 0)),
      Part.LineSegment(App.Vector(2, 0), App.Vector(2, -1)),
      Part.ArcOfCircle(Part.Circle(), math.pi * 1.5, 0),
      Part.LineSegment(App.Vector(1, -2), App.Vector(-1, -2)),
      Part.ArcOfCircle(Part.Circle(), math.pi, math.pi * 1.5),
    ], False)

  pcb_details_s.addConstraint([
    Sketcher.Constraint('Coincident', detail_bl, CA.CENTER, extern_pocket_left, CA.START_POINT),
    Sketcher.Constraint('Coincident', detail_br, CA.CENTER, extern_pocket_right, CA.START_POINT),
    Sketcher.Constraint('Coincident', detail_l, CA.END_POINT, detail_t, CA.START_POINT),
    Sketcher.Constraint('Coincident', detail_t, CA.END_POINT, detail_r, CA.START_POINT),
    Sketcher.Constraint('Tangent', detail_r, CA.END_POINT, detail_br, CA.END_POINT),
    Sketcher.Constraint('Tangent', detail_l, CA.START_POINT, detail_bl, CA.START_POINT),
    Sketcher.Constraint('Tangent', detail_b, CA.START_POINT, detail_br, CA.START_POINT),
    Sketcher.Constraint('Tangent', detail_b, CA.END_POINT, detail_bl, CA.END_POINT),
    Sketcher.Constraint('Vertical', detail_l),
    Sketcher.Constraint('Vertical', detail_r),
    Sketcher.Constraint('PointOnObject', *ORIGIN, detail_t),
    Sketcher.Constraint('Horizontal', detail_t, CA.START_POINT, detail_t, CA.END_POINT)
  ])

  addExpressionConstraint(pcb_details_s, 'Radius', f'{Params.PCB_SERVO_CLEARANCE} + {Params.PCB_OUTLINE_TOLERANCE}', detail_br)
  addExpressionConstraint(pcb_details_s, 'Radius', f'{Params.PCB_SERVO_CLEARANCE} + {Params.PCB_OUTLINE_TOLERANCE}', detail_bl)
  pcb_details_s.recompute()

  pcb_detailed = pcb_base.newObject("PartDesign::Pocket", "PCB_Detailed")
  pcb_detailed.Profile = pcb_details_s
  pcb_detailed.Type = 1
  pcb_detailed.recompute()

  # Export DXF
  def exportDXF(source_obj, path: str):
    face = max([f for f in source_obj.Shape.Faces if f.Surface.isPlanar()], key=lambda f: f.Area)
    face_normal = face.Surface.Axis
    projection = Draft.make_shape2dview(pcb_detailed, projectionVector=face_normal)
    projection.Placement.Rotation = App.Rotation(App.Vector(0, 0, 1), 90)
    projection_bbox_center = projection.Shape.BoundBox.Center
    projection.Placement.Base = projection_bbox_center

    # FIMXE: Part::Part2DObjectPython: Link(s) to object(s) 'PCB_Detailed' go out of the allowed scope 'Shape2DView'.
    # Instead, the linked object(s) reside within 'PCB_Base PCB_Base'.
    projection.recompute()

    importDXF.export([projection], path)

  exportDXF(pcb_detailed, "exports/pcb-outline.dxf")

  return tower_back_cut


# Temporary cap (for tunnel testing)
def createTempCap(doc):
  # Create body for round bases
  cap_bottom = doc.addObject("PartDesign::Body", "Cap_Bottom")

  binder_tower_top_center = cap_bottom.newObject("PartDesign::SubShapeBinder", f"Binder_{tower_top_center.Label}")
  binder_tower_top_center.Support = tower_top_center

  bearing_cylinder = cap_bottom.newObject("PartDesign::AdditiveCylinder", "Cap_Bearing_Cylinder")
  bearing_cylinder.AttachmentSupport = tower_top_center
  bearing_cylinder.MapMode = 'Translate'
  bearing_cylinder.Radius = 22
  bearing_cylinder.setExpression('AttachmentOffset.Base.z', Params.CAP_BASE_HEIGHT)
  bearing_cylinder.setExpression('Height', f'{Params.WINDSHAFT_TO_CAP_TOP_VER}+{Params.WINDSHAFT_TO_CAP_BASE_VER}-{Params.CAP_BASE_HEIGHT}')

  bearing_chamfer = cap_bottom.newObject("PartDesign::Chamfer", "Cap_Bearing_Chamfer")
  bearing_chamfer.Base = (bearing_cylinder, "Edge2")
  bearing_chamfer.Size = 4.5

  base_cylinder = cap_bottom.newObject("PartDesign::AdditiveCylinder", "Cap_Base_Cylinder")
  base_cylinder.AttachmentSupport = tower_top_center
  base_cylinder.MapMode = 'Translate'
  base_cylinder.setExpression('Radius', f'{Params.CAP_BASE_DIAM}/2')
  base_cylinder.setExpression('Height', Params.CAP_BASE_HEIGHT)

  # FIXME: Needed for split?
  doc.RecomputesFrozen = False
  doc.recompute()
  doc.RecomputesFrozen = True

  cap_slice = SplitFeatures.makeSlice(name='Cap_Slice')
  cap_slice.Mode = 'Split'
  cap_slice.Base = cap_bottom
  cap_slice.Tools = [back_plane, windshaft_front_plane]
  cap_slice.recompute()

  cap_filter = CompoundFilter.makeCompoundFilter(name = 'Cap_Slice_Filter')
  cap_filter.Base = cap_slice
  cap_filter.FilterType = 'specific items'
  cap_filter.items = '0'

  return cap_filter


# Cap
def createCap(doc):
  # Create body for round bases
  cap_bottom = doc.addObject("PartDesign::Body", "Cap_Bottom")

  binder_tower_top_center = cap_bottom.newObject("PartDesign::SubShapeBinder", f"Binder_{tower_top_center.Label}")
  binder_tower_top_center.Support = tower_top_center

  # Cap base (bearing core rests on the base)
  base_s = cap_bottom.newObject("Sketcher::SketchObject", "Cap_Base")
  base_s.AttachmentSupport = tower_top_center
  base_s.MapMode = 'Translate'

  # There will be a loft between cap base and bearing for 3D printing
  loft_height_expr = f'({Params.CAP_BEARING_DIAM} - {Params.CAP_BASE_DIAM})/2'
  base_height_expr = f'{Params.CAP_BASE_HEIGHT} - ({loft_height_expr})/2'
  base_s.setExpression('AttachmentOffset.Base.z', base_height_expr)

  base_c = base_s.addGeometry(Part.Circle(App.Vector(), App.Vector(0, 0, 1), 1))
  addExpressionConstraint(base_s, 'Diameter', Params.CAP_BASE_DIAM, base_c)
  base_s.recompute()

  base_pad = cap_bottom.newObject('PartDesign::Pad','Cap_Base_Pad')
  base_pad.Profile = base_s
  base_pad.Reversed = True
  base_pad.setExpression('Length', base_height_expr)

  # Cap bearing core
  bearing_s = cap_bottom.newObject("Sketcher::SketchObject", "Cap_Bearing")
  bearing_s.AttachmentSupport = tower_top_center
  bearing_s.MapMode = 'Translate'
  bearing_s.setExpression('AttachmentOffset.Base.z', f'{Params.CAP_BASE_HEIGHT} + ({loft_height_expr})/2')

  bearing_c = bearing_s.addGeometry(Part.Circle(App.Vector(), App.Vector(0, 0, 1), 1))
  addExpressionConstraint(bearing_s, 'Diameter', Params.CAP_BEARING_DIAM, bearing_c)
  bearing_s.recompute()

  base_loft = cap_bottom.newObject("PartDesign::AdditiveLoft", "Cap_Base_Loft")
  base_loft.Profile = base_s
  base_loft.Sections = [bearing_s]

  bearing_pad = cap_bottom.newObject('PartDesign::Pad','Cap_Bearing_Pad')
  bearing_pad.Profile = bearing_s
  bearing_pad.setExpression('Length', f'{Params.CAP_BEARING_HEIGHT} - ({loft_height_expr})/2')

  return cap_bottom

# Servo mounting tunnel
def createServoTunnel(doc):
  # Create body for cuts
  servo_tunnel = doc.addObject("PartDesign::Body", "Servo_Tunnel")

  binder_windshaft_plane = servo_tunnel.newObject("PartDesign::SubShapeBinder", f"Binder_{windshaft_front_plane.Label}")
  binder_windshaft_plane.Support = windshaft_front_plane

  binder_back_plane = servo_tunnel.newObject("PartDesign::SubShapeBinder", f"Binder_{back_plane.Label}")
  binder_back_plane.Support = back_plane

  # Base shape
  base_s = servo_tunnel.newObject("Sketcher::SketchObject", "Servo_Tunnel_Base")
  base_s.AttachmentSupport = windshaft_axis
  base_s.MapMode = 'NormalToEdge'
  base_s.setExpression('AttachmentOffset.Base.z', f'{Params.SG90_BUSHING_HEIGHT} - {Params.PLA_EXPANSION}')
  base_s.setExpression('AttachmentOffset.Base.y', f'-{Params.SG90_BASE_DEPTH}/2 + {Params.SG90_BASE_WIDTH}/2')

  addCenteredRectangle(base_s, f'{Params.SG90_BASE_WIDTH} + 2*{Params.PLA_EXPANSION}', f'{Params.SG90_BASE_DEPTH} + 2*{Params.PLA_EXPANSION}', *ORIGIN)
  base_s.recompute()

  base_pad = servo_tunnel.newObject('PartDesign::Pad','Servo_Tunnel_Base_Pad')
  base_pad.Profile = base_s
  base_pad.Length = 100

  # Flange
  flanges_s = servo_tunnel.newObject("Sketcher::SketchObject", "Servo_Tunnel_Flanges")
  flanges_s.AttachmentSupport = windshaft_axis
  flanges_s.MapMode = 'NormalToEdge'
  flanges_s.setExpression('AttachmentOffset.Base.z', f'{Params.SG90_BUSHING_HEIGHT} + {Params.SG90_BASE_HEIGHT} - {Params.SG90_FLANGE_BASE_OFFSET} - {Params.SG90_FLANGE_THICKNESS} - {Params.PLA_EXPANSION}')
  flanges_s.setExpression('AttachmentOffset.Base.y', f'-{Params.SG90_BASE_DEPTH}/2 + {Params.SG90_BASE_WIDTH}/2')

  addCenteredRectangle(flanges_s, f'{Params.SG90_BASE_WIDTH} + 2*{Params.PLA_EXPANSION}', f'{Params.SG90_BASE_DEPTH} + 2*{Params.SG90_FLANGE_DEPTH} + 2*{Params.PLA_EXPANSION}', *ORIGIN)
  flanges_s.recompute()

  flanges_pad = servo_tunnel.newObject('PartDesign::Pad','Servo_Tunnel_Flanges_Pad')
  flanges_pad.Profile = flanges_s
  flanges_pad.Length = 100

  # Bushing
  bushing_s = servo_tunnel.newObject("Sketcher::SketchObject", "Servo_Tunnel_Bushing")
  bushing_s.AttachmentSupport = windshaft_axis
  bushing_s.MapMode = 'NormalToEdge'
  bushing_s.setExpression('AttachmentOffset.Base.z', f'-{Params.PLA_EXPANSION}')
  bushing_s.setExpression('AttachmentOffset.Base.y', f'-{Params.SG90_BASE_DEPTH}/2 + {Params.SG90_BASE_WIDTH}/2')

  (bpoint_t, bpoint_r, bpoint_b) = bushing_s.addGeometry([
    Part.Point(App.Vector(0, 1, 0)),
    Part.Point(App.Vector(1, 0, 0)),
    Part.Point(App.Vector(0, -1, 0))], False)

  addExpressionConstraint(bushing_s, 'DistanceY', f'{Params.SG90_BASE_DEPTH}/2 + {Params.PLA_EXPANSION}', bpoint_t, 1)
  addExpressionConstraint(bushing_s, 'DistanceY', f'{Params.SG90_BASE_DEPTH}/2 - {Params.SG90_GEAR_FROMTOP} - {Params.SG90_GEAR_RADIUS} - {Params.PLA_EXPANSION}', bpoint_b, 1)
  addExpressionConstraint(bushing_s, 'DistanceX', f'{Params.SG90_BASE_WIDTH}/2 + {Params.PLA_EXPANSION}', bpoint_r, 1)
  addExpressionConstraint(bushing_s, 'DistanceY', f'{Params.SG90_BASE_DEPTH}/2 - {Params.SG90_BASE_WIDTH}/2', bpoint_r, 1)
  bushing_s.addConstraint([
    Sketcher.Constraint('PointOnObject', bpoint_t, CA.START_POINT, AxisId.Y),
    Sketcher.Constraint('PointOnObject', bpoint_b, CA.START_POINT, AxisId.Y),
  ])
  bushing_s.recompute()

  (brect_ta, brect_ba, brect_l, brect_r) = bushing_s.addGeometry([
    Part.Arc(App.Vector(1, 0, 0), App.Vector(0, 1, 0), App.Vector(-1, 0, 0)),
    Part.Arc(App.Vector(1, 0, 0), App.Vector(0, -1, 0), App.Vector(-1, 0, 0)),
    Part.LineSegment(App.Vector(-1, 0, 0), App.Vector(-1, 1, 0)),
    Part.LineSegment(App.Vector(1, 0, 0), App.Vector(1, 1, 0))], False)

  bushing_s.addConstraint([
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
  bushing_s.recompute()

  addExpressionConstraint(bushing_s, 'DistanceX', f'{Params.SG90_GEAR_RADIUS}*2 + 2*{Params.PLA_EXPANSION}', brect_ta, CA.END_POINT, brect_ta, CA.START_POINT)
  addExpressionConstraint(bushing_s, 'Radius', f'{Params.SG90_GEAR_RADIUS} + {Params.PLA_EXPANSION}', brect_ba)
  bushing_s.recompute()

  bushing_pad = servo_tunnel.newObject('PartDesign::Pad','Servo_Tunnel_Bushing_Pad')
  bushing_pad.Profile = bushing_s
  bushing_pad.Length = 100

  front_cylinder = servo_tunnel.newObject("PartDesign::AdditiveCylinder", "Servo_Tunnel_Front_Cylinder")
  front_cylinder.AttachmentSupport = windshaft_axis
  front_cylinder.MapMode = 'NormalToEdge'
  front_cylinder.MapReversed = True
  front_cylinder.Height = 100
  front_cylinder.setExpression('Radius', f'4 mm + {Params.PLA_EXPANSION}')


tower = createTower(doc)
cap = createCap(doc)
tunnel = createServoTunnel(doc)

# Combine windmill components
windmill_base = doc.addObject("Part::MultiFuse", "Windmill_Base")
windmill_base.Shapes = [tower, cap]
windmill = BOPFeatures(App.activeDocument()).make_cut(["Windmill_Base", "Servo_Tunnel"])

doc.RecomputesFrozen = False
doc.recompute()
doc.saveAs("exports/enclosure.FCStd")

# Export STL

# High-definition mesh parameters (tune as needed)
linear_deflection = 0.01   # mm (smaller = finer)
angular_deflection = math.radians(0.5)  # radians (smaller = finer)
relative = False

# Create mesh from the Part shape
windmill_mesh = MeshPart.meshFromShape(Shape=windmill.Shape,
                                      LinearDeflection=linear_deflection,
                                      AngularDeflection=angular_deflection,
                                      Relative=relative)

# Put mesh into a document object (required for Mesh.export)
mesh_obj = doc.addObject('Mesh::Feature', 'Windmill_Mesh_HD')
mesh_obj.Mesh = windmill_mesh
doc.recompute()

# Export to STL (binary by default). Change path to your desired output.
Mesh.export([mesh_obj], 'exports/enclosure.stl')
