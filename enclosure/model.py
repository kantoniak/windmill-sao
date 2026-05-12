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

IMPORT_STEP = False
EXPORT_STL = False

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
  'WINDSHAFT_TO_ROOF_TOP_VER': '15.4 mm',
  'TOWER_TOP_WIDTH': '36 mm',
  'TOWER_BOTTOM_WIDTH': '56 mm',
  'PCB_THICKNESS': '1.6 mm',
  'PCB_OUTLINE_TOLERANCE': '0.2 mm',
  'PCB_SERVO_CLEARANCE': '1 mm',
  'PCB_MOUNTING_HOLE_DIAM': '2 mm',
  'PCB_MOUNTING_HOLE_X': '11.3 mm',
  'PCB_MOUNTING_HOLE_Y': '4.2 mm',
  'HEAT_INSERT_HOLE_DIAM': '3.2 mm',
  'HEAT_INSERT_HOLE_DEPTH': '15 mm',
  'CAP_BASE_DIAM': '35 mm',
  'CAP_BASE_HEIGHT': '1.25 mm',
  'CAP_BEARING_DIAM': '36.5 mm',
  'CAP_BEARING_HEIGHT': '4.25 mm',
  'CAP_FLOOR_DIAM': '40.5 mm',
  'CAP_FLOOR_HEIGHT': '2.75 mm',
  'BREAST_OUTWARD_DIST': '20.75 mm',
  'BREAST_OUTWARD_WIDTH': '20 mm',
  'BREAST_OUTWARD_HEIGHT': '3 mm',
  'BREAST_INWARD_WIDTH': '21.5 mm',
  'REAR_GABLE_OUTWARD_WIDTH': '24 mm',
  'REAR_GABLE_INWARD_WIDTH': '25 mm',
  'CAP_BASE_TO_ROOF_TOP_HOR': '13 mm',
  'CAP_BASE_TO_ROOF_A_HOR': '11.5 mm',
  'CAP_BASE_TO_ROOF_B_HOR': '5.5 mm',
  'CAP_BASE_TO_ROOF_B_VER': '26 mm',
  'CAP_BASE_TO_REAR_GABLE_TOP_VER': '15 mm',
  'ROOF_TOP_TO_FRONT_PLATE_TOP_VER': '10 mm',
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

"""
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
"""

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
tower_bottom_center.setExpression('Placement.Base', f'vector(0; {Params.WINDSHAFT_TO_CAP_BASE_HOR}; {Params.WINDSHAFT_TO_ROOF_TOP_VER}-{Params.TOTAL_HEIGHT})')

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

  # FIXME: BSpline control points are not available in FreeCAD v1.0 (see above).
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
  surfaces.append(toSurfaceFromSketchEdges(tower_surfaces, tower_top_s))
  surfaces.append(toSurfaceFromSketchEdges(tower_surfaces, tower_bottom_s))

  # Create tower solid

  # FIXME: Surfaces don't have Faces if the doc is not recomputed. It looks like surfaces from a single sketch can
  # actually recompute themselved. How to skip this recompute?
  doc.RecomputesFrozen = False
  doc.recompute()
  doc.RecomputesFrozen = True

  tower_solid = doc.addObject("Part::Feature", "Tower_Solid")
  tower_solid.Shape = Part.makeSolid(Part.makeShell([s.Shape.Faces[0] for s in surfaces]))

  # Create tower base (not source accurate, just for visual finish at the bottom)
  tower_base = doc.addObject("PartDesign::Body", "Tower_Base")

  binder_tower_bottom_s = tower_base.newObject("PartDesign::ShapeBinder", f"Binder_{tower_bottom_s.Label}")
  binder_tower_bottom_s.Support = tower_bottom_s

  tower_base_pad = tower_base.newObject("PartDesign::Pad", "Tower_Base_Pad")
  tower_base_pad.Profile = binder_tower_bottom_s
  tower_base_pad.Length = 4

  # Build window casing
  def createWindowSketch(parent, name: str):
    sketch = parent.newObject("Sketcher::SketchObject", name)
    sketch.AttachmentSupport = tower_top_back
    sketch.MapMode = 'ObjectXZ'
    sketch.setExpression('AttachmentOffset.Rotation.Angle', '180 deg')
    sketch.setExpression('AttachmentOffset.Rotation.Axis', u'vector(0; 1; 0)')

    geometry = sketch.addGeometry([
      Part.LineSegment(App.Vector(-1, 1), App.Vector(0, 2)),
      Part.LineSegment(App.Vector(0, 2), App.Vector(1, 1)),
      Part.LineSegment(App.Vector(1, 1), App.Vector(1, 0)),
      Part.LineSegment(App.Vector(1, 0), App.Vector(-1, 0)),
      Part.LineSegment(App.Vector(-1, 0), App.Vector(-1, 1)),
    ], False)

    (it_tl, it_tr, it_r, it_b, it_l) = geometry
    sketch.addConstraint(constrainCoincidentPath([it_tl, it_tr, it_r, it_b, it_l], True) + [
      Sketcher.Constraint('PointOnObject', *ORIGIN, it_b),
      Sketcher.Constraint('Symmetric', it_b, CA.START_POINT, it_b, CA.END_POINT, AxisId.Y),
      Sketcher.Constraint('Symmetric', it_r, CA.START_POINT, it_l, CA.END_POINT, AxisId.Y),
      Sketcher.Constraint('Vertical', it_l),
      Sketcher.Constraint('PointOnObject', it_tl, CA.END_POINT, AxisId.Y),
    ])

    addExpressionConstraint(sketch, "Angle", "90 deg", it_tr, CA.END_POINT, it_tl, CA.START_POINT)
    sketch.recompute()
    return (sketch, geometry)

  tower_window_casing = doc.addObject("PartDesign::Body", "Tower_Window_Casing")

  (tower_window_casing_s, tower_window_casing_s_geom) = createWindowSketch(tower_window_casing, f"{tower_window_casing.Label}_S")
  tower_window_casing_s.setExpression('AttachmentOffset.Base.y', f'-1*1 mm + (1.5 mm + {Params.WINDSHAFT_TO_ROOF_TOP_VER} - {Params.TOTAL_HEIGHT} + {Params.WINDSHAFT_TO_CAP_BASE_VER}) + ({Params.PCB_THICKNESS} + {Params.PLA_EXPANSION} + 6 mm - {Params.PCB_THICKNESS} - {Params.PLA_EXPANSION}) + 19.53 mm')
  tower_window_casing_s.setExpression('AttachmentOffset.Base.z', f'{Params.PCB_THICKNESS} + {Params.PLA_EXPANSION} + 6 mm + 19.53 mm ')

  (c_it_tl, _, _, c_it_b, _) = tower_window_casing_s_geom
  addExpressionConstraint(tower_window_casing_s, "DistanceX", f'5 mm + 2*1mm', c_it_b, CA.START_POINT, c_it_b, CA.END_POINT)
  addExpressionConstraint(tower_window_casing_s, "DistanceY", f'7 mm + 1mm + sqrt(2)*1mm', *ORIGIN, c_it_tl, CA.END_POINT)
  tower_window_casing_s.recompute()

  tower_window_casing_pad = tower_window_casing.newObject('PartDesign::Pad', f"{tower_window_casing.Label}_Pad")
  tower_window_casing_pad.Profile = tower_window_casing_s
  tower_window_casing_pad.Type = 'TwoLengths'
  tower_window_casing_pad.setExpression('Length', f'1.5 mm') # Arbitrary
  tower_window_casing_pad.setExpression('Length2', f'0.5 mm') # Arbitrary

  tower_fuse = doc.addObject("Part::MultiFuse", "Tower_Fuse")
  tower_fuse.Shapes = [tower_solid, tower_window_casing, tower_base]

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

  # Cut the components compartment
  # There is a "cyclic" dependency between generated PCB shape and the space we have to cut out for components.
  tower_inner = doc.addObject("PartDesign::Body", "Tower_Inner")

  tower_inner_base = tower_inner.newObject("PartDesign::Pad", f"{tower_inner.Label}_Base")
  tower_inner_base.Profile = tower_back_offset
  tower_inner_base.Reversed = True
  tower_inner_base.setExpression('Length', f'{Params.PCB_THICKNESS} + {Params.PLA_EXPANSION} + 6 mm')

  tower_inner_top_s = tower_inner.newObject("Sketcher::SketchObject", f"{tower_inner.Label}_Top")
  tower_inner_top_s.AttachmentSupport = tower_top_back
  tower_inner_top_s.MapMode = 'ObjectXZ'
  tower_inner_top_s.setExpression('AttachmentOffset.Rotation.Angle', '180 deg')
  tower_inner_top_s.setExpression('AttachmentOffset.Rotation.Axis', u'vector(0; 1; 0)')
  tower_inner_top_s.setExpression('AttachmentOffset.Base.z', f'<<{tower_inner_base.Label}>>.Length')

  (it_t, it_r, it_br, it_bl, it_l) = tower_inner_top_s.addGeometry([
      Part.LineSegment(App.Vector(-1, 0), App.Vector(1, 0)),
      Part.LineSegment(App.Vector(1, 0), App.Vector(1, -2)),
      Part.LineSegment(App.Vector(1, -2), App.Vector(0, -1)),
      Part.LineSegment(App.Vector(0, -1), App.Vector(-1, -2)),
      Part.LineSegment(App.Vector(-1, -2), App.Vector(-1, 0)),
    ], False)

  tower_inner_top_s.addConstraint(constrainCoincidentPath([it_t, it_r, it_br, it_bl, it_l], True) + [
    Sketcher.Constraint('PointOnObject', *ORIGIN, it_t),
    Sketcher.Constraint('Symmetric', it_t, CA.START_POINT, it_t, CA.END_POINT, AxisId.Y),
    Sketcher.Constraint('Symmetric', it_r, CA.END_POINT, it_l, CA.START_POINT, AxisId.Y),
    Sketcher.Constraint('Vertical', it_l),
    Sketcher.Constraint('PointOnObject', it_br, CA.END_POINT, AxisId.Y),
  ])

  addExpressionConstraint(tower_inner_top_s, "Angle", "90 deg", it_bl, CA.END_POINT, it_br, CA.START_POINT)
  addExpressionConstraint(tower_inner_top_s, "DistanceX", f'{Params.TOWER_BOTTOM_WIDTH}', it_t, CA.START_POINT, it_t, CA.END_POINT)
  addExpressionConstraint(tower_inner_top_s, "DistanceY", f'5 mm', it_br, CA.END_POINT, *ORIGIN) # Based on fixed attachment offset
  tower_inner_top_s.recompute()

  tower_inner_top_pocket = tower_inner.newObject("PartDesign::Pocket", f"{tower_inner.Label}_Top_Pocket")
  tower_inner_top_pocket.Profile = tower_inner_top_s
  tower_inner_top_pocket.Reversed = True
  tower_inner_top_pocket.Type = 1

  tower_inner_bottom_sbox = tower_inner.newObject("PartDesign::SubtractiveBox", f'{tower_inner.Label}_SBox')
  tower_inner_bottom_sbox.AttachmentSupport = [back_plane, tower_bottom_center]
  tower_inner_bottom_sbox.MapMode = 'TangentPlane'
  tower_inner_bottom_sbox.setExpression('AttachmentOffset.Base.x', f'-{Params.TOWER_BOTTOM_WIDTH}/2')
  tower_inner_bottom_sbox.setExpression('AttachmentOffset.Rotation.Angle', '180 deg')
  tower_inner_bottom_sbox.setExpression('AttachmentOffset.Rotation.Axis', u'vector(1; 0; 0)')
  tower_inner_bottom_sbox.MapReversed = True
  tower_inner_bottom_sbox.setExpression('Length', f'10 mm') # Arbitrary
  tower_inner_bottom_sbox.setExpression('Width', f'<<{tower_base_pad.Name}>>.Length')
  tower_inner_bottom_sbox.setExpression('Height', f'<<{tower_inner_base.Name}>>.Length')

  tower_inner_bottom_sbox_mirror = tower_inner.newObject("PartDesign::Mirrored", f"{tower_inner_bottom_sbox.Label}_Mirror")
  tower_inner_bottom_sbox_mirror.Originals = tower_inner_bottom_sbox
  tower_inner_bottom_sbox_mirror.MirrorPlane = tower_inner.Origin.OriginFeatures[5]
  tower_inner.Tip = tower_inner_bottom_sbox_mirror

  # Build window tunnel
  (tower_window_tunnel_s, tower_window_tunnel_s_geom) = createWindowSketch(tower_inner, f"Tower_Window_Tunnel")
  tower_window_tunnel_s.setExpression('AttachmentOffset.Base.y', f'19.53 mm + (1.5 mm + {Params.WINDSHAFT_TO_ROOF_TOP_VER} - {Params.TOTAL_HEIGHT} + {Params.WINDSHAFT_TO_CAP_BASE_VER}) + (<<{tower_inner_base.Label}>>.Length - {Params.PCB_THICKNESS} - {Params.PLA_EXPANSION})')
  tower_window_tunnel_s.setExpression('AttachmentOffset.Base.z', f'19.53 mm + <<{tower_inner_base.Label}>>.Length')

  (w_it_tl, _, _, w_it_b, _) = tower_window_tunnel_s_geom
  addExpressionConstraint(tower_window_tunnel_s, "DistanceX", f'5 mm', w_it_b, CA.START_POINT, w_it_b, CA.END_POINT)
  addExpressionConstraint(tower_window_tunnel_s, "DistanceY", f'7 mm', *ORIGIN, w_it_tl, CA.END_POINT)
  tower_window_tunnel_s.recompute()

  tower_window_tunnel_pad = tower_inner.newObject('PartDesign::Pad', f'Tower_Window_Tunnel_Pad')
  tower_window_tunnel_pad.Profile = tower_window_tunnel_s
  tower_window_tunnel_pad.UseCustomVector = 1
  tower_window_tunnel_pad.Direction = (0, -1, 1)
  tower_window_tunnel_pad.AlongSketchNormal = 1
  tower_window_tunnel_pad.Reversed = 1
  tower_window_tunnel_pad.setExpression('Length', f'19.53 mm') # Arbitrary

  tower_window_tunnel_pad2 = tower_inner.newObject('PartDesign::Pad', f"Tower_Window_Tunnel_Pad2")
  tower_window_tunnel_pad2.Profile = tower_window_tunnel_s
  tower_window_tunnel_pad2.Reversed = 1
  tower_window_tunnel_pad2.setExpression('Length', f'0.5 mm') # Arbitrary

  # Cut out components compartment
  tower_inner_cut = doc.addObject("Part::Cut", "Tower_Inner_Cut")
  tower_inner_cut.Base = tower_back_cut
  tower_inner_cut.Tool = tower_inner

  # Cut out the QWIIC connector tunnel
  tower_side_tunnel = doc.addObject("PartDesign::Body", "Tower_Side_Tunnel")

  tower_qwiic = tower_side_tunnel.newObject("PartDesign::AdditiveBox", "Tower_QWIIC")
  tower_qwiic.AttachmentSupport = tower_top_back
  tower_qwiic.MapMode = 'ObjectXY'
  tower_qwiic.MapReversed = True
  tower_qwiic.setExpression('AttachmentOffset.Base.x', f'15 mm -{Params.TOWER_BOTTOM_WIDTH}/2')
  tower_qwiic.setExpression('AttachmentOffset.Base.y', f'-Width')
  tower_qwiic.setExpression('AttachmentOffset.Base.z', f'-13.5 mm -({Params.WINDSHAFT_TO_ROOF_TOP_VER} - {Params.TOTAL_HEIGHT} + {Params.WINDSHAFT_TO_CAP_BASE_VER})')
  tower_qwiic.setExpression('AttachmentOffset.Rotation.Angle', '-107 deg')
  tower_qwiic.setExpression('AttachmentOffset.Rotation.Axis', u'vector(0; 1; 0)')
  tower_qwiic.setExpression('Width', f'5.5 mm') # Measured ~4.56
  tower_qwiic.setExpression('Height', f'40 mm')
  tower_qwiic.setExpression('Length', f'8 mm') # Measured 6

  tower_side_cut = doc.addObject("Part::Cut", "Tower_Side_Cut")
  tower_side_cut.Base = tower_inner_cut
  tower_side_cut.Tool = tower_side_tunnel

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

  pcb = doc.addObject("PartDesign::Body", "PCB")
  binder_pcb_offset = pcb.newObject("PartDesign::ShapeBinder", f"Binder_{pcb_offset.Label}")
  binder_pcb_offset.Support = pcb_offset

  pcb_pad = pcb.newObject("PartDesign::Pad", "PCB_Pad")
  pcb_pad.Profile = binder_pcb_offset
  pcb_pad.Reversed = True
  pcb_pad.setExpression('Length', f'{Params.PCB_THICKNESS}')

  binder_pcb_tunnel_container = pcb.newObject("PartDesign::ShapeBinder", f"Binder_{tower_tunnelb_s.Name}")
  binder_pcb_tunnel_container.Support = tower_tunnelb_s

  pcb_pocket = pcb.newObject("PartDesign::Pocket", "PCB_Pocket")
  pcb_pocket.Profile = binder_pcb_tunnel_container
  pcb_pocket.Type = 1
  pcb_pocket.Reversed = True

  # FIXME: Required for pocket, can we skip this?
  doc.RecomputesFrozen = False
  doc.recompute()
  doc.RecomputesFrozen = True

  pcb_details_s = pcb.newObject("Sketcher::SketchObject", "PCB_Details")
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
      Part.ArcOfCircle(Part.Circle(App.Vector(), App.Vector(0, 0, 1), 1), math.pi * 1.5, 0),
      Part.LineSegment(App.Vector(1, -2), App.Vector(-1, -2)),
      Part.ArcOfCircle(Part.Circle(App.Vector(), App.Vector(0, 0, 1), 1), math.pi, math.pi * 1.5),
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

  pcb_detailed = pcb.newObject("PartDesign::Pocket", "PCB_Detailed")
  pcb_detailed.Profile = pcb_details_s
  pcb_detailed.Type = 1

  def createPCBMountingHoleSketch(name: str, parent, diameter_expr: str):
    sketch = parent.newObject("Sketcher::SketchObject", name)
    sketch.AttachmentSupport = tower_top_back
    sketch.MapMode = 'ObjectXZ'
    sketch.MapReversed = True

    (insert_c,) = sketch.addGeometry([
      Part.Circle(App.Vector(), App.Vector(0, 0, 1), 1)
    ], False)

    addExpressionConstraint(sketch, 'Diameter', diameter_expr, insert_c)
    addExpressionConstraint(sketch, 'DistanceX', f'{Params.PCB_MOUNTING_HOLE_X}', insert_c, CA.CENTER, *ORIGIN)
    addExpressionConstraint(sketch, 'DistanceY', f'{Params.PCB_MOUNTING_HOLE_Y}', insert_c, CA.CENTER, *ORIGIN)
    sketch.recompute()
    return sketch

  # Add heat insert holes
  tower_heat_insert = doc.addObject("PartDesign::Body", "Tower_Heat_Insert")
  tower_heat_insert_s = createPCBMountingHoleSketch('Heat_Insert_Hole', tower_heat_insert, f'{Params.HEAT_INSERT_HOLE_DIAM}')
  tower_heat_insert_hole = tower_heat_insert.newObject("PartDesign::Pocket", "Heat_Insert_Hole_Pocket")
  tower_heat_insert_hole.Profile = tower_heat_insert_s
  tower_heat_insert_hole.Type = 'Length'
  tower_heat_insert_hole.setExpression('Length', f'{Params.HEAT_INSERT_HOLE_DEPTH} + {Params.PCB_THICKNESS} + {Params.PLA_EXPANSION}')

  tower_heat_insert_mirror = doc.addObject('Part::Mirroring', 'Tower_Heat_Insert_Mirror')
  tower_heat_insert_mirror.Source = tower_heat_insert
  tower_heat_insert_mirror.Normal = (1, 0, 0)

  tower_heat_insert_holes = doc.addObject('Part::Compound', 'Tower_Heat_Insert_Holes')
  tower_heat_insert_holes.Links = [tower_heat_insert, tower_heat_insert_mirror]

  tower = doc.addObject("Part::Cut", "Tower")
  tower.Base = tower_side_cut
  tower.Tool = tower_heat_insert_holes

  # Add PCB mounting holes
  pcb_mounting_hole_s = createPCBMountingHoleSketch('PCB_Mounting_Hole', pcb, f'{Params.PCB_MOUNTING_HOLE_DIAM}')
  pcb_mounting_hole = pcb.newObject("PartDesign::Pocket", "PCB_Mounting_Hole_Pocket")
  pcb_mounting_hole.Profile = pcb_mounting_hole_s
  pcb_mounting_hole.Type = 'ThroughAll'

  pcb_mounting_hole_mirror = pcb.newObject("PartDesign::Mirrored", "PCB_Mounting_Hole_Mirror")
  pcb_mounting_hole_mirror.Originals = pcb_mounting_hole
  pcb_mounting_hole_mirror.MirrorPlane = pcb.Origin.OriginFeatures[5]
  pcb.Tip = pcb_mounting_hole_mirror

  # Export DXF
  def exportDXF(source_obj, path: str):
    planar_faces = [f for f in source_obj.Shape.Faces if f.Surface.isPlanar()]
    if not planar_faces:
      raise ValueError('No planar faces available for DXF export')

    reference_face = max(planar_faces, key=lambda f: f.Area)
    reference_axis = reference_face.Surface.Axis
    reference_center = reference_face.BoundBox.Center

    def is_coplanar(face):
      axis = face.Surface.Axis
      if abs(abs(axis.dot(reference_axis)) - 1.0) > 1e-6:
        return False
      face_center = face.BoundBox.Center
      return abs(reference_axis.dot(face_center - reference_center)) < 1e-6

    coplanar_faces = [f for f in planar_faces if is_coplanar(f)]

    projection_source = doc.addObject('Part::Feature', 'PCB_DXF_Projection_Source')
    projection_source.Shape = Part.Compound(coplanar_faces)

    projection = Draft.make_shape2dview(projection_source, projectionVector=reference_axis)
    projection.Label = f'{source_obj.Label}_DXF'
    projection.Placement.Rotation = App.Rotation(App.Vector(0, 0, 1), 90)
    projection_bbox_center = projection.Shape.BoundBox.Center
    projection.Placement.Base = projection_bbox_center
    projection.recompute()
    source_obj.addObject(projection)

    importDXF.export([projection], path)
    doc.removeObject(projection_source.Name)

  doc.RecomputesFrozen = False
  doc.recompute()
  doc.RecomputesFrozen = True
  exportDXF(pcb, "exports/pcb-outline.dxf")

  return tower


# Cap
def createCap(doc):
  cap_objects = doc.addObject("App::DocumentObjectGroup", "Cap_Objects")

  # Create body for round bases
  cap_bottom = cap_objects.newObject("PartDesign::Body", "Cap_Bottom")

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

  # Create body for sketch-based top
  cap_top = cap_objects.newObject("App::DocumentObjectGroup", "Cap_Top")

  # Top geometry
  cap_floor_center = cap_top.newObject("PartDesign::Point", "Cap_Floor_Center")
  cap_floor_center.MapMode = 'Deactivated'
  cap_floor_center.setExpression('Placement.Base.y', Params.WINDSHAFT_TO_CAP_BASE_HOR)
  cap_floor_center.setExpression('Placement.Base.z', f'-{Params.WINDSHAFT_TO_CAP_BASE_VER} + {Params.CAP_BASE_HEIGHT} + {Params.CAP_BEARING_HEIGHT} + {Params.CAP_FLOOR_HEIGHT}')

  cap_floor_centerline = cap_top.newObject("PartDesign::Line", "Cap_Floor_Centerline")
  cap_floor_centerline.AttachmentSupport = cap_floor_center
  cap_floor_centerline.MapMode = 'ObjectY'

  roof_ridge_top = cap_top.newObject("PartDesign::Point", "Roof_Ridge_Top")
  roof_ridge_top.MapMode = 'Translate'
  roof_ridge_top.setExpression('Placement.Base.y', f'{Params.WINDSHAFT_TO_CAP_BASE_HOR} - {Params.CAP_BASE_TO_ROOF_TOP_HOR}')
  roof_ridge_top.setExpression('Placement.Base.z', Params.WINDSHAFT_TO_ROOF_TOP_VER)

  roof_ridge_b = cap_top.newObject("PartDesign::Point", "Roof_Ridge_B")
  roof_ridge_b.MapMode = 'Translate'
  roof_ridge_b.setExpression('Placement.Base.y', f'{Params.WINDSHAFT_TO_CAP_BASE_HOR} + {Params.CAP_BASE_TO_ROOF_B_HOR}')
  roof_ridge_b.setExpression('Placement.Base.z', f'-{Params.WINDSHAFT_TO_CAP_BASE_VER} + {Params.CAP_BASE_TO_ROOF_B_VER}')

  roof_ridge_a = cap_top.newObject("PartDesign::Point", "Roof_Ridge_A")
  roof_ridge_a.MapMode = 'Translate'
  roof_ridge_a.setExpression('Placement.Base.y', f'{Params.WINDSHAFT_TO_CAP_BASE_HOR} - {Params.CAP_BASE_TO_ROOF_A_HOR}')
  roof_ridge_a.setExpression('Placement.Base.z', 'Roof_Ridge_Top.Placement.Base.z + (Placement.Base.y - Roof_Ridge_Top.Placement.Base.y) * (Roof_Ridge_B.Placement.Base.z - Roof_Ridge_Top.Placement.Base.z) / (Roof_Ridge_B.Placement.Base.y - Roof_Ridge_Top.Placement.Base.y)')

  rear_gable_top = cap_top.newObject("PartDesign::Point", "Rear_Gable_Top")
  rear_gable_top.MapMode = 'Deactivated'
  rear_gable_top.setExpression('Placement.Base.y', f'{Params.WINDSHAFT_TO_CAP_BASE_HOR} + ({Params.CAP_FLOOR_DIAM}/2)')
  rear_gable_top.setExpression('Placement.Base.z', f'-{Params.WINDSHAFT_TO_CAP_BASE_VER} + {Params.CAP_BASE_TO_REAR_GABLE_TOP_VER}')

  breast_front_top = cap_top.newObject("PartDesign::Point", "Breast_Front_Top")
  breast_front_top.AttachmentSupport = cap_floor_center
  breast_front_top.MapMode = "ObjectOrigin"
  breast_front_top.setExpression('AttachmentOffset.Base.y', f'-{Params.BREAST_OUTWARD_DIST}')
  breast_front_top.setExpression('AttachmentOffset.Base.z', f'{Params.BREAST_OUTWARD_HEIGHT}')

  # Floor sketch, with edges separated at the roof ridge stops
  floor_s = cap_top.newObject("Sketcher::SketchObject", "Cap_Floor_Top")
  floor_s.AttachmentSupport = cap_floor_center
  floor_s.MapMode = 'ObjectXY'
  floor_s.setExpression('AttachmentOffset.Rotation.Angle', '90 deg')

  floor_geometry = floor_s.addGeometry([
      Part.LineSegment(App.Vector(-3, 0), App.Vector(-3, 1)),
      Part.LineSegment(App.Vector(-3, 1), App.Vector(-2, 1)),
      # Solver has a hard time if the circle below is centered at (-2, 2)
      Part.ArcOfCircle(Part.Circle(App.Vector(-20, 15), App.Vector(0, 0, 1), 1), math.pi * 1.5, 0),
      Part.ArcOfCircle(Part.Circle(App.Vector(0, 2), App.Vector(0, 0, 1), 1), 0, math.pi * 0.25),
      Part.ArcOfCircle(Part.Circle(App.Vector(0, 2), App.Vector(0, 0, 1), 1), math.pi * 0.25, math.pi * 0.75),
      Part.ArcOfCircle(Part.Circle(App.Vector(0, 2), App.Vector(0, 0, 1), 1), math.pi * 0.75, math.pi),
      # Solver has a hard time if the circle below is centered at (2, 2)
      Part.ArcOfCircle(Part.Circle(App.Vector(-20, 35), App.Vector(0, 0, 1), 1), math.pi, math.pi * 1.5),
      Part.LineSegment(App.Vector(2, 1), App.Vector(3, 1)),
      Part.LineSegment(App.Vector(3, 1), App.Vector(3, 0)),
      Part.LineSegment(App.Vector(3, 0), App.Vector(-3, 0)),
    ], False)
  (floor_l, floor_tl, floor_al, floor_atl, floor_atc, floor_atr, floor_ar, floor_tr, floor_r, floor_b) = floor_geometry

  extern_ridge_a = addExternalGeomIndexed(floor_s, roof_ridge_a, 'Vertex1')
  extern_ridge_b = addExternalGeomIndexed(floor_s, roof_ridge_b, 'Vertex1')

  floor_s.addConstraint(constrainCoincidentPath([floor_tr, floor_r, floor_b, floor_l, floor_tl]) + [
    Sketcher.Constraint('Vertical', floor_l),
    Sketcher.Constraint('Vertical', floor_r),
    Sketcher.Constraint('Horizontal', floor_b),
    Sketcher.Constraint('Vertical', extern_ridge_a, CA.START_POINT, floor_atc, CA.END_POINT),
    Sketcher.Constraint('Vertical', extern_ridge_b, CA.START_POINT, floor_atc, CA.START_POINT),
    Sketcher.Constraint('Coincident', floor_atl, CA.CENTER, *ORIGIN),
    Sketcher.Constraint('Coincident', floor_atc, CA.CENTER, *ORIGIN),
    Sketcher.Constraint('Coincident', floor_atr, CA.CENTER, *ORIGIN),
    Sketcher.Constraint('PointOnObject', floor_b, CA.START_POINT, AxisId.X),
  ])
  floor_s.recompute()

  floor_s.addConstraint([
    Sketcher.Constraint('Tangent', floor_tl, CA.END_POINT, floor_al, CA.START_POINT),
    Sketcher.Constraint('Tangent', floor_al, CA.END_POINT, floor_atl, CA.END_POINT),
    Sketcher.Constraint('Tangent', floor_atr, CA.START_POINT, floor_ar, CA.START_POINT),
    Sketcher.Constraint('Tangent', floor_ar, CA.END_POINT, floor_tr, CA.START_POINT),
  ])

  floor_s_constr_diam_atl = addExpressionConstraint(floor_s, 'Diameter', Params.CAP_FLOOR_DIAM, floor_atl)
  floor_s_constr_diam_atc = addExpressionConstraint(floor_s, 'Diameter', Params.CAP_FLOOR_DIAM, floor_atc)
  floor_s_constr_diam_atr = addExpressionConstraint(floor_s, 'Diameter', Params.CAP_FLOOR_DIAM, floor_atr)
  addExpressionConstraint(floor_s, 'DistanceX', Params.BREAST_OUTWARD_DIST, floor_l, CA.START_POINT, *ORIGIN)
  addExpressionConstraint(floor_s, 'DistanceY', f'{Params.BREAST_OUTWARD_WIDTH}/2', *ORIGIN, floor_l, CA.END_POINT)
  addExpressionConstraint(floor_s, 'DistanceX', f'{Params.CAP_BEARING_DIAM}/2', floor_tl, CA.END_POINT, *ORIGIN)
  addExpressionConstraint(floor_s, 'DistanceY', f'{Params.BREAST_INWARD_WIDTH}/2', *ORIGIN, floor_tl, CA.END_POINT)
  addExpressionConstraint(floor_s, 'DistanceX', f'{Params.CAP_FLOOR_DIAM}/2', *ORIGIN, floor_r, CA.START_POINT)
  addExpressionConstraint(floor_s, 'DistanceY', f'{Params.REAR_GABLE_OUTWARD_WIDTH}/2', *ORIGIN, floor_r, CA.START_POINT)
  addExpressionConstraint(floor_s, 'DistanceX', f'{Params.CAP_BEARING_DIAM}/2', *ORIGIN, floor_tr, CA.START_POINT)
  addExpressionConstraint(floor_s, 'DistanceY', f'{Params.REAR_GABLE_INWARD_WIDTH}/2', *ORIGIN, floor_tr, CA.START_POINT)
  floor_s.recompute()

  floor_s.delConstraint(floor_s_constr_diam_atr)
  floor_s.delConstraint(floor_s_constr_diam_atl)
  floor_s.addConstraint([
    Sketcher.Constraint('Coincident', floor_atl, CA.START_POINT, floor_atc, CA.END_POINT),
    Sketcher.Constraint('Coincident', floor_atc, CA.START_POINT, floor_atr, CA.END_POINT),
  ])
  floor_s.recompute()

  # Cap floor
  cap_floor = cap_top.newObject("PartDesign::Body", "Cap_Floor")

  binder_floor_s = cap_floor.newObject("PartDesign::ShapeBinder", f"Binder_{floor_s.Label}")
  binder_floor_s.Support = floor_s

  floor_pad = cap_floor.newObject('PartDesign::Pad', 'Cap_Floor_Pad')
  floor_pad.Profile = binder_floor_s
  floor_pad.Reversed = True
  floor_pad.setExpression('Length', Params.CAP_FLOOR_HEIGHT)

  floor_chamfer = cap_floor.newObject('PartDesign::Chamfer', 'Cap_Floor_Chamfer')
  floor_chamfer.Base = (floor_pad, ['Edge16'])
  floor_chamfer.setExpression('Size', f'{Params.BREAST_OUTWARD_DIST} - ({Params.CAP_BEARING_DIAM}/2)')

  # Roof rib A
  rib_a_s = cap_top.newObject("Sketcher::SketchObject", "Roof_Rib_A")
  rib_a_s.AttachmentSupport = [cap_floor_centerline, roof_ridge_a]
  rib_a_s.MapMode = 'ParallelPlane'

  extern_side_a = addExternalGeomIndexed(rib_a_s, floor_s, 'Vertex5')
  extern_ridge_a = addExternalGeomIndexed(rib_a_s, roof_ridge_a, 'Point')

  (rib_a_arc, rib_a_lt, rib_a_lb) = rib_a_s.addGeometry([
    Part.ArcOfCircle(Part.Circle(App.Vector(20, -10, 0), App.Vector(0, 0, 1), 21), math.pi / 2, math.pi),
    Part.LineSegment(App.Vector(0, 1, 0), App.Vector(0, 0, 0)),
    Part.LineSegment(App.Vector(-1, 0, 0), App.Vector(0, 0, 0)),
  ], False)

  rib_a_constraints = rib_a_s.addConstraint([
    Sketcher.Constraint('Coincident', rib_a_arc, CA.START_POINT, extern_ridge_a, CA.START_POINT),
    Sketcher.Constraint('Coincident', rib_a_arc, CA.END_POINT, extern_side_a, CA.START_POINT),
    Sketcher.Constraint('Coincident', rib_a_lt, CA.START_POINT, extern_ridge_a, CA.START_POINT),
    Sketcher.Constraint('Coincident', rib_a_lt, CA.END_POINT, rib_a_arc, CA.CENTER),
    Sketcher.Constraint('Coincident', rib_a_lb, CA.START_POINT, extern_side_a, CA.START_POINT),
    Sketcher.Constraint('Coincident', rib_a_lb, CA.END_POINT, rib_a_arc, CA.CENTER),
    Sketcher.Constraint('Angle', rib_a_lt, CA.START_POINT, rib_a_lb, CA.START_POINT, math.radians(59))
  ])

  rib_a_s.toggleConstruction(rib_a_lb)
  rib_a_s.toggleConstruction(rib_a_lt)
  rib_a_s.setDatum(rib_a_constraints[-1], App.Units.Quantity('59 deg'))
  rib_a_s.recompute()

  # Roof rib B
  rib_b_s = cap_top.newObject("Sketcher::SketchObject", "Roof_Rib_B")
  rib_b_s.AttachmentSupport = [cap_floor_centerline, roof_ridge_b]
  rib_b_s.MapMode = 'ParallelPlane'

  # FIXME: This is a really weird bug. Everything EXCEPT Vertex6 gets correctly linked. Using Edge6 instead.
  extern_side_b = addExternalGeomIndexed(rib_b_s, floor_s, 'Edge6')
  extern_ridge_b = addExternalGeomIndexed(rib_b_s, roof_ridge_b, 'Point')

  (rib_b_arc, rib_b_lt, rib_b_lb) = rib_b_s.addGeometry([
    Part.ArcOfCircle(Part.Circle(App.Vector(20, -10, 0), App.Vector(0, 0, 1), 21), math.pi / 2, math.pi),
    Part.LineSegment(App.Vector(0, 1, 0), App.Vector(0, 0, 0)),
    Part.LineSegment(App.Vector(-1, 0, 0), App.Vector(0, 0, 0)),
  ], False)

  rib_b_constraints = rib_b_s.addConstraint([
    Sketcher.Constraint('Coincident', rib_b_arc, CA.START_POINT, extern_ridge_b, CA.START_POINT),
    Sketcher.Constraint('Coincident', rib_b_arc, CA.END_POINT, extern_side_b, CA.END_POINT),
    Sketcher.Constraint('Coincident', rib_b_lt, CA.START_POINT, extern_ridge_b, CA.START_POINT),
    Sketcher.Constraint('Coincident', rib_b_lt, CA.END_POINT, rib_b_arc, CA.CENTER),
    Sketcher.Constraint('Coincident', rib_b_lb, CA.START_POINT, extern_side_b, CA.END_POINT),
    Sketcher.Constraint('Coincident', rib_b_lb, CA.END_POINT, rib_b_arc, CA.CENTER),
    Sketcher.Constraint('Angle', rib_b_lt, CA.END_POINT, rib_b_lb, CA.END_POINT, math.radians(40))
  ])

  rib_b_s.toggleConstruction(rib_b_lb)
  rib_b_s.toggleConstruction(rib_b_lt)
  rib_b_s.setDatum(rib_b_constraints[-1], App.Units.Quantity('40 deg'))
  rib_b_s.recompute()

  # Breast front
  breast_front_s = cap_top.newObject("Sketcher::SketchObject", "Breast_Front")
  breast_front_s.AttachmentSupport = breast_front_top
  breast_front_s.MapMode = "ObjectXZ"

  (breast_f1, breast_f2, breast_f3, breast_f4) = breast_front_s.addGeometry([
    Part.LineSegment(App.Vector(0, 0, 0),  App.Vector(-1, 0, 0)),   # horizontal left
    Part.LineSegment(App.Vector(-1, 0, 0), App.Vector(-1, -1, 0)),  # vertical down
    Part.LineSegment(App.Vector(-1, -1, 0), App.Vector(0, -1, 0)),  # horizontal right
    Part.LineSegment(App.Vector(0, -1, 0),  App.Vector(0, 0, 0)),   # vertical up
  ], False)

  breast_front_s.addConstraint(constrainCoincidentPath([breast_f1, breast_f2, breast_f3, breast_f4], True) + [
    Sketcher.Constraint("Coincident", breast_f1, CA.START_POINT, *ORIGIN),
    Sketcher.Constraint("Horizontal", breast_f1),
    Sketcher.Constraint("Horizontal", breast_f3),
    Sketcher.Constraint("Vertical",   breast_f2),
    Sketcher.Constraint("Vertical",   breast_f4),
  ])
  addExpressionConstraint(breast_front_s, "DistanceX", f'{Params.BREAST_OUTWARD_WIDTH}/2', breast_f2, CA.END_POINT, *ORIGIN)
  addExpressionConstraint(breast_front_s, "DistanceY", f'{Params.BREAST_OUTWARD_HEIGHT}', breast_f2, CA.END_POINT, *ORIGIN)
  breast_front_s.recompute()

  # Roof front
  roof_front_s = cap_top.newObject("Sketcher::SketchObject", "Roof_Front")
  roof_front_s.AttachmentSupport = [breast_front_top, roof_ridge_top]
  roof_front_s.MapMode = "OYZ"

  extern_top = addExternalGeomIndexed(roof_front_s, roof_ridge_top, "Point")

  (front_h, front_slant, front_v, front_arc) = roof_front_s.addGeometry([
    Part.LineSegment(App.Vector(0,0,0), App.Vector(-1,0,0)),
    Part.LineSegment(App.Vector(-1,0,0), App.Vector(-1,1,0)),
    Part.LineSegment(App.Vector(0,0,0), App.Vector(0,1,0)),
    Part.ArcOfCircle(Part.Circle(App.Vector(5,0,0), App.Vector(0,0,1), 1), math.pi/2, math.pi),
  ], False)
  roof_front_s.toggleConstruction(front_slant)

  roof_front_s.addConstraint([
    Sketcher.Constraint('Coincident', front_h, CA.START_POINT, *ORIGIN),
    Sketcher.Constraint('Horizontal', front_h),
    Sketcher.Constraint('Coincident', front_v, CA.START_POINT, *ORIGIN),
    Sketcher.Constraint('Coincident', front_v, CA.END_POINT, extern_top, CA.START_POINT),
    Sketcher.Constraint('Coincident', front_h, CA.END_POINT, front_slant, CA.START_POINT),
    Sketcher.Constraint('PointOnObject', front_slant, CA.END_POINT, AxisId.Y),
    Sketcher.Constraint('Coincident', front_arc, CA.START_POINT, extern_top, CA.START_POINT),
    Sketcher.Constraint('Coincident', front_arc, CA.END_POINT, front_h, CA.END_POINT),
    Sketcher.Constraint('PointOnObject', front_arc, CA.CENTER, AxisId.X),
  ])

  addExpressionConstraint(roof_front_s, "DistanceX", f'{Params.BREAST_OUTWARD_WIDTH}/2', front_h, CA.END_POINT, *ORIGIN)
  addExpressionConstraint(roof_front_s, "Angle", "60 deg", front_h, CA.START_POINT, front_slant, CA.END_POINT)

  roof_front_s.recompute()

  # Roof ridge (full loop)
  roof_ridge_s = cap_top.newObject("Sketcher::SketchObject", "Roof_Ridge")
  roof_ridge_s.AttachmentSupport = cap_floor_center
  roof_ridge_s.MapMode = "ObjectYZ"

  extern_ridge_top = addExternalGeomIndexed(roof_ridge_s, roof_ridge_top, "Point")
  extern_ridge_a = addExternalGeomIndexed(roof_ridge_s, roof_ridge_a, "Point")
  extern_ridge_b = addExternalGeomIndexed(roof_ridge_s, roof_ridge_b, "Point")
  extern_ridge_rear = addExternalGeomIndexed(roof_ridge_s, rear_gable_top, "Point")
  extern_breast_top = addExternalGeomIndexed(roof_ridge_s, breast_front_top, "Point")

  (ridge_ta, ridge_ab, ridge_br, ridge_rb, ridge_bf, ridge_fb, ridge_bt) = roof_ridge_s.addGeometry([
    Part.LineSegment(App.Vector(0,0,0), App.Vector(1,0,0)),
    Part.LineSegment(App.Vector(1,0,0), App.Vector(2,0,0)),
    Part.LineSegment(App.Vector(2,0,0), App.Vector(3,0,0)),
    Part.LineSegment(App.Vector(3,0,0), App.Vector(3,-1,0)),
    Part.LineSegment(App.Vector(3,-1,0), App.Vector(-1, -1,0)),
    Part.LineSegment(App.Vector(-1,-1,0), App.Vector(-1,0,0)),
    Part.LineSegment(App.Vector(-1,0,0), App.Vector(0,0,0)),
  ], False)

  roof_ridge_s.addConstraint(constrainCoincidentPath([ridge_ta, ridge_ab, ridge_br, ridge_rb, ridge_bf, ridge_fb, ridge_bt], True) + [
    Sketcher.Constraint('Coincident', ridge_ta, CA.START_POINT, extern_ridge_top, CA.START_POINT),
    Sketcher.Constraint('Coincident', ridge_ta, CA.END_POINT, extern_ridge_a, CA.START_POINT),
    Sketcher.Constraint('Coincident', ridge_ab, CA.END_POINT, extern_ridge_b, CA.START_POINT),
    Sketcher.Constraint('Coincident', ridge_br, CA.END_POINT, extern_ridge_rear, CA.START_POINT),
    Sketcher.Constraint('Coincident', ridge_fb, CA.END_POINT, extern_breast_top, CA.START_POINT),
    Sketcher.Constraint('PointOnObject', ridge_fb, CA.START_POINT, AxisId.X),
    Sketcher.Constraint('Vertical', ridge_rb),
    Sketcher.Constraint('Vertical', ridge_fb),
    Sketcher.Constraint('Horizontal', ridge_bf),
  ])
  roof_ridge_s.recompute()

  # Rear gable
  rear_gable_back_s = cap_top.newObject("Sketcher::SketchObject", "Rear_Gable_Back")
  rear_gable_back_s.AttachmentSupport = rear_gable_top
  rear_gable_back_s.MapMode = "ObjectXZ"

  rear_gable_extern_cap_floor_center = addExternalGeomIndexed(rear_gable_back_s, cap_floor_center, "Point")

  (rear_g1, rear_g2, rear_g3, rear_g4) = rear_gable_back_s.addGeometry([
    Part.LineSegment(App.Vector(0, 0, 0),  App.Vector(-1, 0, 0)),   # horizontal left
    Part.LineSegment(App.Vector(-1, 0, 0), App.Vector(-1, -1, 0)),  # vertical down
    Part.LineSegment(App.Vector(-1, -1, 0), App.Vector(0, -1, 0)),  # horizontal right
    Part.LineSegment(App.Vector(0, -1, 0),  App.Vector(0, 0, 0)),   # vertical up
  ], False)

  rear_gable_back_s.addConstraint(constrainCoincidentPath([rear_g1, rear_g2, rear_g3, rear_g4]) + [
    Sketcher.Constraint("Coincident", rear_g1, CA.START_POINT, *ORIGIN),
    Sketcher.Constraint("Coincident", rear_g4, CA.START_POINT, rear_gable_extern_cap_floor_center, CA.START_POINT),
    Sketcher.Constraint("Coincident", rear_g4, CA.END_POINT, *ORIGIN),
    Sketcher.Constraint("Horizontal", rear_g1),
    Sketcher.Constraint("Horizontal", rear_g3),
    Sketcher.Constraint("Vertical",   rear_g2),
  ])
  addExpressionConstraint(rear_gable_back_s, "DistanceX", f'{Params.REAR_GABLE_OUTWARD_WIDTH}/2', rear_g2, CA.END_POINT, *ORIGIN)
  rear_gable_back_s.recompute()

  # Rear gable to roof ridge point B edge
  rear_gable_to_a_s = cap_top.newObject("Sketcher::SketchObject", "Rear_Gable_To_A")
  rear_gable_to_a_s.AttachmentSupport = [rear_gable_top, (rear_gable_back_s, "Vertex2"), roof_ridge_b]
  rear_gable_to_a_s.MapMode = "OXY"

  rear_gable_extern_roof_ridge_b = addExternalGeomIndexed(rear_gable_to_a_s, roof_ridge_b, "Point")
  rear_gable_extern_gable_top_outwards = addExternalGeomIndexed(rear_gable_to_a_s, rear_gable_back_s, "Vertex2")
  rear_gable_extern_gable_top = addExternalGeomIndexed(rear_gable_to_a_s, rear_gable_top, "Point")

  (rg_to_a_v, rg_to_a_s, rg_to_a_h) = rear_gable_to_a_s.addGeometry([
    Part.LineSegment(App.Vector(0,0,0), App.Vector(1,0,0)),
    Part.LineSegment(App.Vector(1,0,0), App.Vector(0,1,0)),
    Part.LineSegment(App.Vector(0,1,0), App.Vector(0,0,0)),
  ], False)
  rear_gable_to_a_s.addConstraint(constrainCoincidentPath([rg_to_a_v, rg_to_a_s, rg_to_a_h], True) + [
    Sketcher.Constraint('Coincident', rg_to_a_v, CA.END_POINT, rear_gable_extern_roof_ridge_b, CA.START_POINT),
    Sketcher.Constraint('Coincident', rg_to_a_s, CA.END_POINT, rear_gable_extern_gable_top_outwards, CA.START_POINT),
    Sketcher.Constraint('Coincident', rg_to_a_h, CA.END_POINT, rear_gable_extern_gable_top, CA.START_POINT),
  ])
  rear_gable_to_a_s.recompute()

  # Roof surfaces
  print("Creating roof surfaces, this may take a while...")
  roof_surfaces = cap_top.newObject("App::DocumentObjectGroup", "Roof_Surfaces")

  # FIXME: Need to recompute doc to avoid TNP issues.
  doc.RecomputesFrozen = False
  doc.recompute()
  doc.RecomputesFrozen = True

  # Roof side surface
  surface_roof_side = roof_surfaces.newObject("Surface::Filling", "Surface_Roof_Side")
  surface_roof_side.BoundaryEdges = [
    (floor_s, "Edge2"),
    (floor_s, "Edge3"),
    (floor_s, "Edge4"),
    (floor_s, "Edge5"),
    (floor_s, "Edge6"),
    (floor_s, "Edge7"),
    (floor_s, "Edge8"),
    (rear_gable_back_s, "Edge2"),
    (rear_gable_to_a_s, "Edge2"),
    (roof_ridge_s, "Edge2"),
    (roof_ridge_s, "Edge1"),
    (roof_front_s, "Edge2"),
    (breast_front_s, "Edge2"),
  ]
  surface_roof_side.UnboundEdges = [
    (rib_b_s, "Edge1"),
    (rib_a_s, "Edge1"),
  ]
  surface_roof_side.Degree = 2
  surface_roof_side.Iterations = 2
  surface_roof_side.recompute()

  # Supporting flat faces
  roof_sketches = [
    breast_front_s,
    roof_front_s,
    roof_ridge_s,
    rear_gable_to_a_s,
    rear_gable_back_s,
    floor_s,
  ]
  surfaces = [toSurfaceFromSketchEdges(roof_surfaces, s) for s in roof_sketches]
  surfaces.append(surface_roof_side)
  print("Created roof surfaces.")

  # Roof solid
  doc.RecomputesFrozen = False
  doc.recompute()
  doc.RecomputesFrozen = True

  roof_solid = cap_top.newObject("Part::Feature", "Roof_Solid")
  roof_solid.Shape = Part.makeSolid(Part.makeShell([s.Shape.Faces[0] for s in surfaces]))

  # Cap forward compound
  cap_forward_group = cap_top.newObject("App::DocumentObjectGroup", "Cap_Forward_Group")

  cap_forward = cap_forward_group.newObject("PartDesign::Body", "Cap_Forward")
  binder_roof_ridge_top = cap_forward.newObject("PartDesign::SubShapeBinder", f"Binder_{roof_ridge_top.Label}")
  binder_roof_ridge_top.Support = roof_ridge_top
  binder_roof_ridge_top.recompute()

  # Front view
  cap_forward_s = cap_forward.newObject("Sketcher::SketchObject", "Cap_Forward_Front")
  cap_forward_s.AttachmentSupport = [breast_front_top, binder_roof_ridge_top]
  cap_forward_s.MapMode = "OYZ"

  cap_forward_extern_top = addExternalGeomIndexed(cap_forward_s, binder_roof_ridge_top, "Vertex1")

  (cfwd_h, cfwd_v, cfwd_arc) = cap_forward_s.addGeometry([
    Part.LineSegment(App.Vector(0,0,0), App.Vector(-1,0,0)),
    Part.LineSegment(App.Vector(0,0,0), App.Vector(0,1,0)),
    Part.ArcOfCircle(Part.Circle(App.Vector(5,0,0), App.Vector(0,0,1), 1), math.pi/2, math.pi),
  ], False)

  cap_forward_s.addConstraint([
    Sketcher.Constraint('Coincident', cfwd_h, CA.START_POINT, *ORIGIN),
    Sketcher.Constraint('Horizontal', cfwd_h),
    Sketcher.Constraint('Coincident', cfwd_v, CA.START_POINT, *ORIGIN),
    Sketcher.Constraint('Coincident', cfwd_v, CA.END_POINT, cap_forward_extern_top, CA.START_POINT),
    Sketcher.Constraint('Coincident', cfwd_arc, CA.START_POINT, cap_forward_extern_top, CA.START_POINT),
    Sketcher.Constraint('Coincident', cfwd_arc, CA.END_POINT, cfwd_h, CA.END_POINT),
    Sketcher.Constraint('PointOnObject', cfwd_arc, CA.CENTER, AxisId.X),
  ])

  addExpressionConstraint(cap_forward_s, "DistanceX", f'{Params.BREAST_OUTWARD_WIDTH}/2', cfwd_h, CA.END_POINT, *ORIGIN)
  cap_forward_s.recompute()

  # Side view
  cap_forward_side_s = cap_forward.newObject("Sketcher::SketchObject", "Cap_Forward_Side")
  cap_forward_side_s.AttachmentSupport = [breast_front_top, binder_roof_ridge_top]
  cap_forward_side_s.MapMode = "ObjectYZ"

  cap_forward_extern_top = addExternalGeomIndexed(cap_forward_side_s, binder_roof_ridge_top, "Vertex1")

  (cfwds_b, cfwds_t) = cap_forward_side_s.addGeometry([
    Part.LineSegment(App.Vector(0,0,0), App.Vector(0,1,0)),
    Part.LineSegment(App.Vector(0,1,0), App.Vector(0,2,0)),
  ], False)

  cap_forward_side_s.addConstraint([
    Sketcher.Constraint('Coincident', cfwds_b, CA.START_POINT, *ORIGIN),
    Sketcher.Constraint('Coincident', cfwds_b, CA.END_POINT, cfwds_t, CA.START_POINT),
    Sketcher.Constraint('Coincident', cfwds_t, CA.END_POINT, cap_forward_extern_top, CA.START_POINT),
  ])

  addExpressionConstraint(cap_forward_side_s, "DistanceY", Params.ROOF_TOP_TO_FRONT_PLATE_TOP_VER, cfwds_t, CA.START_POINT, cap_forward_extern_top, CA.START_POINT)
  addExpressionConstraint(cap_forward_side_s, "Angle", Params.WINDSHAFT_TILT, cfwds_b, CA.START_POINT, AxisId.Y, CA.START_POINT)
  cap_forward_side_s.recompute()

  # Pad and slice shape
  cap_forward_pad = cap_forward.newObject('PartDesign::Pad', 'Cap_Forward_Pad')
  cap_forward_pad.Profile = cap_forward_s
  cap_forward_pad.Type = 'Length'
  cap_forward_pad.Length = 5

  cap_forward_plane_b = cap_forward_group.newObject("PartDesign::Plane", "Cap_Forward_Plane_Bottom")
  cap_forward_plane_b.AttachmentSupport = [breast_front_top, (cap_forward_side_s, "Vertex2")]
  cap_forward_plane_b.MapMode = 'OXY'

  cap_forward_plane_t = cap_forward_group.newObject("PartDesign::Plane", "Cap_Forward_Plane_Top")
  cap_forward_plane_t.AttachmentSupport = [(cap_forward_side_s, "Vertex2"), roof_ridge_top]
  cap_forward_plane_t.MapMode = 'OXY'

  doc.RecomputesFrozen = False
  doc.recompute()
  doc.RecomputesFrozen = True

  cap_forward_slice_b = SplitFeatures.makeSlice(name='Cap_Forward_Slice_Bottom')
  cap_forward_group.addObject(cap_forward_slice_b)
  cap_forward_slice_b.Base = cap_forward
  cap_forward_slice_b.Tools = cap_forward_plane_b
  cap_forward_slice_b.Mode = 'Split'
  cap_forward_slice_b.recompute()

  cap_forward_slice_b_result = CompoundFilter.makeCompoundFilter("Cap_Forward_Slice_Bottom_Result", cap_forward_group)
  cap_forward_slice_b_result.Base = cap_forward_slice_b
  cap_forward_slice_b_result.FilterType = "specific items"
  cap_forward_slice_b_result.items = "1"

  doc.RecomputesFrozen = False
  doc.recompute()
  doc.RecomputesFrozen = True

  cap_forward_slice_t = SplitFeatures.makeSlice(name='Cap_Forward_Slice_Top')
  cap_forward_group.addObject(cap_forward_slice_t)
  cap_forward_slice_t.Base = cap_forward_slice_b_result
  cap_forward_slice_t.Tools = cap_forward_plane_t
  cap_forward_slice_t.Mode = 'Split'
  cap_forward_slice_t.recompute()

  cap_forward_slice_t_result = CompoundFilter.makeCompoundFilter("Cap_Forward_Slice_Top_Result", cap_forward_group)
  cap_forward_slice_t_result.Base = cap_forward_slice_t
  cap_forward_slice_t_result.FilterType = "specific items"
  cap_forward_slice_t_result.items = "0"

  # Roof shingles
  cap_forward_shingle = cap_forward_group.newObject("PartDesign::Body", "Cap_Forward_Shingle")

  # Side shingle view
  cap_forward_shingle_side_s = cap_forward_shingle.newObject("Sketcher::SketchObject", "Cap_Forward_Shingle_Side")
  cap_forward_shingle_side_s.AttachmentSupport = [(cap_forward_side_s, "Vertex2"), roof_ridge_top, breast_front_top]
  cap_forward_shingle_side_s.MapMode = "OYX"

  (cfwdsh_out, cfwdsh_back, cfwdsh_in) = cap_forward_shingle_side_s.addGeometry([
    Part.LineSegment(App.Vector(0,0,0), App.Vector(0,1,0)),
    Part.LineSegment(App.Vector(0,1,0), App.Vector(1,1,0)),
    Part.LineSegment(App.Vector(1,1,0), App.Vector(0,0,0)),
  ], False)

  cap_forward_shingle_side_s.addConstraint(constrainCoincidentPath([cfwdsh_out, cfwdsh_back, cfwdsh_in], True) + [
    Sketcher.Constraint('Coincident', cfwdsh_out, CA.START_POINT, *ORIGIN),
    Sketcher.Constraint('Vertical', cfwdsh_out),
  ])
  addExpressionConstraint(cap_forward_shingle_side_s, "Distance", f'{cap_forward_side_s.Label}.Shape.Edges[1].Length / 7', cfwdsh_out, CA.START_POINT, cfwdsh_out, CA.END_POINT)
  addExpressionConstraint(cap_forward_shingle_side_s, "Angle", "6.5 deg", cfwdsh_in, CA.START_POINT, cfwdsh_out, CA.END_POINT)
  addExpressionConstraint(cap_forward_shingle_side_s, "Angle", "90 deg", cfwdsh_back, CA.START_POINT, cfwdsh_in, CA.END_POINT)
  cap_forward_shingle_side_s.recompute()

  # Pad
  cap_forward_shingle_pad = cap_forward_shingle.newObject('PartDesign::Pad', 'Cap_Forward_Shingle_Pad')
  cap_forward_shingle_pad.Profile = cap_forward_shingle_side_s
  cap_forward_shingle_pad.Type = 'Length'
  cap_forward_shingle_pad.Reversed = True
  cap_forward_shingle_pad.setExpression('Length', f'{Params.BREAST_OUTWARD_WIDTH}/2')

  # Path array
  cap_forward_shingles = Draft.make_path_array(
    base_object = cap_forward_shingle_pad,
    path_object = cap_forward_side_s,
    count = 6,
    subelements = ["Edge2"],
    end_offset = 1)
  cap_forward_shingles.setExpression('EndOffset', f'{cap_forward_side_s.Label}.Shape.Edges[1].Length * 2 / 7')
  cap_forward_shingles.Label = "Cap_Forward_Shingles"
  cap_forward_group.addObject(cap_forward_shingles)

  # Cut shingle array from cap forward assembly
  cap_forward_shingle_cut = cap_forward_group.newObject("Part::Cut", "Cap_Forward_Shingle_Cut")
  cap_forward_shingle_cut.Base = cap_forward_slice_t_result
  cap_forward_shingle_cut.Tool = cap_forward_shingles

  # Slice away back of the cap
  doc.RecomputesFrozen = False
  doc.recompute()
  doc.RecomputesFrozen = True

  def sliceWithBackPlane(base, parent, item_index):
    slice = SplitFeatures.makeSlice(f"{base.Label}_Slice")
    parent.addObject(slice)
    slice.Base = base
    slice.Tools = back_plane
    slice.Mode = 'Split'
    slice.recompute()

    slice_result = CompoundFilter.makeCompoundFilter(f"{base.Label}_Slice_Result", parent)
    slice_result.Base = slice
    slice_result.FilterType = "specific items"
    slice_result.items = "0"
    return slice_result

  cap_bottom_slice_result = sliceWithBackPlane(cap_bottom, cap_objects, 0)
  cap_floor_slice_result = sliceWithBackPlane(cap_floor, cap_objects, 0)
  roof_solid_slice_result = sliceWithBackPlane(roof_solid, cap_objects, 0)

  # Group and mirror cap top
  cap_top_mirrored = doc.addObject('Part::Compound', 'Cap_Top_Mirrored')
  cap_top_mirrored.Links = [cap_floor_slice_result, roof_solid_slice_result, cap_forward_shingle_cut]

  cap_top_mirror = doc.addObject('Part::Mirroring', 'Cap_Top_Mirror')
  cap_top_mirror.Source = cap_top_mirrored
  cap_top_mirror.Normal = (1, 0, 0)

  cap_solid = doc.addObject('Part::Compound', 'Cap_Solid')
  cap_solid.Links = [cap_bottom_slice_result, cap_top_mirrored, cap_top_mirror]

  # Cut away a triangular shape to provide support for 3D printing
  cap_back = doc.addObject("PartDesign::Body", "Cap_Back")

  cap_back_s = cap_back.newObject("Sketcher::SketchObject", "Cap_Back_Sketch")
  cap_back_s.AttachmentSupport = tower_top_back
  cap_back_s.MapMode = "ObjectXZ"
  cap_back_s.MapReversed = True

  (bc_b, bc_tr, bc_tl) = cap_back_s.addGeometry([
    Part.LineSegment(App.Vector(-1,0,0), App.Vector(1,0,0)),
    Part.LineSegment(App.Vector(1,0,0), App.Vector(0,1,0)),
    Part.LineSegment(App.Vector(0,1,0), App.Vector(-1,0,0))], False)

  cap_back_s.addConstraint(constrainCoincidentPath([bc_b, bc_tr, bc_tl], True) + [
    Sketcher.Constraint('Symmetric', bc_b, CA.START_POINT, bc_b, CA.END_POINT, AxisId.Y),
    Sketcher.Constraint('PointOnObject', bc_b, CA.START_POINT, AxisId.X),
    Sketcher.Constraint('PointOnObject', bc_tl, CA.START_POINT, AxisId.Y),
    Sketcher.Constraint('Angle', bc_tr, CA.END_POINT, bc_b, CA.START_POINT, math.pi / 4)
  ])
  addExpressionConstraint(cap_back_s, "DistanceX", f'{Params.TOWER_TOP_WIDTH} + (<<Tower_Back_Offset>>.Value * 2 mm)', bc_b, CA.START_POINT, bc_b, CA.END_POINT)
  cap_back_s.recompute()

  cap_back_cut_pad = cap_back.newObject('PartDesign::Pad', 'Cap_Back_Pad')
  cap_back_cut_pad.Profile = cap_back_s
  cap_back_cut_pad.Reversed = True
  cap_back_cut_pad.setExpression('Length', f'<<Tower_Back_Offset_Pad>>.Length')

  cap = doc.addObject("Part::Cut", "Cap")
  cap.Base = cap_solid
  cap.Tool = cap_back

  return cap

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

  return servo_tunnel


def createWindsail(doc):
  windsail_base_point = doc.addObject("PartDesign::Point", "Windsail_Base_Point")
  windsail_base_point.AttachmentSupport = windshaft_axis
  windsail_base_point.MapMode = 'ObjectOrigin'
  windsail_base_point.MapReversed = True
  windsail_base_point.setExpression('AttachmentOffset.Base.z', f'-6 mm')

  # Create mount
  windsail_mount = doc.addObject("PartDesign::Body", "Windsail_Mount")

  windsail_mount_base = windsail_mount.newObject("PartDesign::AdditiveCylinder", f'{windsail_mount.Label}_Base')
  windsail_mount_base.AttachmentSupport = [windsail_base_point, windshaft_axis]
  windsail_mount_base.MapMode = 'ObjectXY'
  windsail_mount_base.setExpression('AttachmentOffset.Base.z', f'-1.75 mm')
  windsail_mount_base.setExpression('Radius', f'3.6 mm')
  windsail_mount_base.setExpression('Height', f'7 mm')

  windsail_mount_teeth = windsail_mount.newObject("PartDesign::SubtractiveCylinder", f'{windsail_mount.Label}_Teeth')
  windsail_mount_teeth.AttachmentSupport = windshaft_axis
  windsail_mount_teeth.MapMode = 'ObjectXY'
  windsail_mount_teeth.setExpression('Radius', f'2.5 mm') # TEETH RADIUS
  windsail_mount_teeth.setExpression('Height', f'3.4 mm')

  windsail_mount_front = windsail_mount.newObject("PartDesign::SubtractiveCylinder", f'{windsail_mount.Label}_Front')
  windsail_mount_front.AttachmentSupport = windshaft_axis
  windsail_mount_front.MapMode = 'ObjectXY'
  windsail_mount_front.setExpression('AttachmentOffset.Base.z', f'4.9 mm')
  windsail_mount_front.setExpression('Radius', f'2.7 mm')
  windsail_mount_front.setExpression('Height', f'50 mm')

  windsail_mount_passthrough = windsail_mount.newObject("PartDesign::SubtractiveCylinder", f'{windsail_mount.Label}_Passthrough')
  windsail_mount_passthrough.AttachmentSupport = windshaft_axis
  windsail_mount_passthrough.MapMode = 'ObjectXY'
  windsail_mount_passthrough.setExpression('Radius', f'1.25 mm')
  windsail_mount_passthrough.setExpression('Height', f'50 mm')

  windsail_mount_arm = windsail_mount.newObject("PartDesign::AdditiveBox", f'{windsail_mount.Label}_Arm')
  windsail_mount_arm.AttachmentSupport = [windsail_base_point, windshaft_axis]
  windsail_mount_arm.MapMode = 'ObjectXY'
  windsail_mount_arm.MapReversed = True
  windsail_mount_arm.setExpression('AttachmentOffset.Base.x', f'3 mm')
  windsail_mount_arm.setExpression('AttachmentOffset.Base.y', f'-0.8 mm')
  windsail_mount_arm.setExpression('AttachmentOffset.Base.z', f'0.75 mm')
  windsail_mount_arm.setExpression('Length', f'3 mm')
  windsail_mount_arm.setExpression('Width', f'1.6 mm')
  windsail_mount_arm.setExpression('Height', f'1 mm')

  # FIXME: Link out of allowed scope but binder doesn't work as axis
  windsail_mount_arms = windsail_mount.newObject("PartDesign::PolarPattern", f'{windsail_mount.Label}_Arms')
  windsail_mount_arms.Originals = [windsail_mount_arm]
  windsail_mount_arms.Axis = (windshaft_axis, [''])
  windsail_mount_arms.Occurrences = 4
  windsail_mount.Tip = windsail_mount_arms

  # Create stocks
  def createStockBox(parent, object_name: str, rotation_angle: int):
    stock = parent.newObject("PartDesign::AdditiveBox", object_name)
    stock.AttachmentSupport = [windsail_base_point, windshaft_axis]
    stock.MapMode = 'NormalToEdge'
    stock.MapReversed = True
    stock.setExpression('Length', f'57 mm * 2')
    stock.setExpression('Width', f'4 mm')
    stock.setExpression('Height', f'2 mm')
    stock.setExpression('AttachmentOffset.Base.z', f'0.75 mm')

    groove = parent.newObject("PartDesign::SubtractiveBox", f'{object_name}_Groove')
    groove.AttachmentSupport = [windsail_base_point, windshaft_axis]
    groove.MapMode = 'ObjectXY'
    groove.MapReversed = True
    groove.setExpression('Length', f'(6 mm + {Params.PLA_EXPANSION})*2')
    groove.setExpression('Width', f'1.6 mm + 2*{Params.PLA_EXPANSION}')
    groove.setExpression('Height', f'1 mm + {Params.PLA_EXPANSION}')
    groove.setExpression('AttachmentOffset.Base.z', f'0.75 mm')

    match rotation_angle:
      case 0:
        stock.setExpression('AttachmentOffset.Base.x', f'-57 mm')
        stock.setExpression('AttachmentOffset.Base.y', f'-(4 mm / 2)')
        groove.setExpression('AttachmentOffset.Base.x', f'-6 mm - {Params.PLA_EXPANSION}')
        groove.setExpression('AttachmentOffset.Base.y', f'-0.8 mm - {Params.PLA_EXPANSION}')

      case 90:
        stock.setExpression('AttachmentOffset.Base.y', f'-57 mm')
        stock.setExpression('AttachmentOffset.Base.x', f'(4 mm / 2)')
        stock.setExpression('AttachmentOffset.Rotation.Angle', f'{rotation_angle} deg')
        stock.AttachmentOffset.Rotation.Axis = App.Vector(0, 0, 1)
        groove.setExpression('AttachmentOffset.Base.y', f'-6 mm - {Params.PLA_EXPANSION}')
        groove.setExpression('AttachmentOffset.Base.x', f'0.8 mm + {Params.PLA_EXPANSION}')
        groove.setExpression('AttachmentOffset.Rotation.Angle', f'{rotation_angle} deg')
        groove.AttachmentOffset.Rotation.Axis = App.Vector(0, 0, 1)

      case _:
        raise NotImplementedError

    return stock

  windsail_stocks = doc.addObject("PartDesign::Body", "Windsail_Stocks")

  windsail_stocks_center = windsail_stocks.newObject("PartDesign::AdditiveCylinder", f'{windsail_stocks.Label}_Center')
  windsail_stocks_center.AttachmentSupport = [windsail_base_point, windshaft_axis]
  windsail_stocks_center.MapMode = 'ObjectXY'
  windsail_stocks_center.MapReversed = True
  windsail_stocks_center.setExpression('AttachmentOffset.Base.z', f'0.75 mm')
  windsail_stocks_center.setExpression('Radius', f'3.6 mm + 0.2 mm + 1 mm')
  windsail_stocks_center.setExpression('Height', f'2 mm + 0.25 mm')

  windsail_stock_x = createStockBox(windsail_stocks, "Windsail_StockX", rotation_angle = 0)
  windsail_stock_y = createStockBox(windsail_stocks, "Windsail_StockY", rotation_angle = 90)

  windsail_stocks_hole = windsail_stocks.newObject("PartDesign::SubtractiveCylinder", f'{windsail_stocks.Label}_Hole')
  windsail_stocks_hole.AttachmentSupport = [windsail_base_point, windshaft_axis]
  windsail_stocks_hole.MapMode = 'ObjectXY'
  windsail_stocks_hole.MapReversed = True
  windsail_stocks_hole.setExpression('AttachmentOffset.Base.z', f'0.75 mm')
  windsail_stocks_hole.setExpression('Radius', f'3.6 mm + 0.2 mm')
  windsail_stocks_hole.setExpression('Height', f'1 mm + {Params.PLA_EXPANSION}')

  windsail_stocks_passthrough = windsail_stocks.newObject("PartDesign::SubtractiveCylinder", f'{windsail_stocks.Label}_Passthrough')
  windsail_stocks_passthrough.AttachmentSupport = [windsail_base_point, windshaft_axis]
  windsail_stocks_passthrough.MapMode = 'ObjectXY'
  windsail_stocks_passthrough.MapReversed = True
  windsail_stocks_passthrough.setExpression('Radius', f'1.25 mm')
  windsail_stocks_passthrough.setExpression('Height', f'50 mm')

  # Sailbars
  windsail_sailbar = doc.addObject("Part::Compound", "Windsail_Sailbair")

  def addSingleSailbarSharedProperties(obj):
    obj.AttachmentSupport = [windsail_base_point, windshaft_axis]
    obj.MapMode = 'ObjectXY'
    obj.MapReversed = True
    obj.setExpression('Length', f'0.8 mm')
    obj.setExpression('Width', f'0.8 mm')
    obj.setExpression('Height', f'3 mm')

  windsail_sailbar_y_long = doc.addObject("Part::Box", "Windsail_SailbarY_Long")
  addSingleSailbarSharedProperties(windsail_sailbar_y_long)
  windsail_sailbar_y_long.setExpression('Width', f'12.2 mm')
  windsail_sailbar_y_long.setExpression('AttachmentOffset.Base.x', f'12 mm')
  windsail_sailbar_y_long.setExpression('AttachmentOffset.Base.y', f'-12.2 mm + 2 mm')

  windsail_sailbar_y_short = doc.addObject("Part::Box", "Windsail_SailbarY_Short")
  addSingleSailbarSharedProperties(windsail_sailbar_y_short)
  windsail_sailbar_y_short.setExpression('Width', f'4.6 mm')
  windsail_sailbar_y_short.setExpression('AttachmentOffset.Base.x', f'12 mm')
  windsail_sailbar_y_short.setExpression('AttachmentOffset.Base.y', f'-0.8 mm + 2mm')

  windsail_sailbar_x_top = doc.addObject("Part::Box", "Windsail_SailbarX_Top")
  addSingleSailbarSharedProperties(windsail_sailbar_x_top)
  windsail_sailbar_x_top.setExpression('Length', f'57 mm - 12 mm')
  windsail_sailbar_x_top.setExpression('AttachmentOffset.Base.x', f'12 mm')
  windsail_sailbar_x_top.setExpression('AttachmentOffset.Base.y', f'4.6 mm + 0.4 mm')

  windsail_sailbar_x_mid = doc.addObject("Part::Box", "Windsail_SailbarX_Mid")
  addSingleSailbarSharedProperties(windsail_sailbar_x_mid)
  windsail_sailbar_x_mid.setExpression('Length', f'57 mm - 12 mm')
  windsail_sailbar_x_mid.setExpression('AttachmentOffset.Base.x', f'12 mm')
  windsail_sailbar_x_mid.setExpression('AttachmentOffset.Base.y', f'-0.8 mm + 2mm')

  def createSailbarPathArray(obj, count: int, distance_expr: str, alongY: bool = False):
    # Create sketch (path)
    path_s = doc.addObject("Sketcher::SketchObject", f"{obj.Name}_Path")
    path_s.AttachmentSupport = [windsail_base_point, windshaft_axis]
    path_s.MapMode = 'ObjectXY'
    path_s.MapReversed = True
    path_s.setExpression('AttachmentOffset', f'<<{obj.Name}>>.AttachmentOffset')

    line_end_vector = App.Vector(0,-1,0) if alongY else App.Vector(1,0,0)
    (line,) = path_s.addGeometry([
      Part.LineSegment(App.Vector(0,0,0), line_end_vector),
    ], False)

    path_s.addConstraint([
      Sketcher.Constraint('Coincident', line, CA.START_POINT, *ORIGIN),
      Sketcher.Constraint('Vertical' if alongY else 'Horizontal', line),
    ])

    addExpressionConstraint(path_s, "Distance", distance_expr, line, CA.START_POINT, line, CA.END_POINT)
    path_s.recompute()

    # Create path array
    path_array = Draft.make_path_array(
      base_object = obj,
      path_object = path_s,
      count = count,
      subelements = ["Edge1"],
      end_offset = 1)
    path_array.setExpression('EndOffset', f'0.8 mm')
    path_array.Label = f"{obj.Name}_PathArray"

    return (path_s, path_array)

  (windsail_sailbar_y_long_path_s, windsail_sailbar_y_long_pattern) = createSailbarPathArray(windsail_sailbar_y_long, 16, "57 mm - 12 mm")
  (windsail_sailbar_y_short_path_s, windsail_sailbar_y_short_pattern) = createSailbarPathArray(windsail_sailbar_y_short, 11, "57 mm - 12 mm")
  (windsail_sailbar_x_mid_path_s, windsail_sailbar_x_mid_pattern) = createSailbarPathArray(windsail_sailbar_x_mid, 4, "12.2 mm", alongY=True)

  windsail_sailbar.Links = [
    windsail_sailbar_x_top,
    windsail_sailbar_x_mid_pattern,
    windsail_sailbar_y_long_pattern,
    windsail_sailbar_y_short_pattern]

  windsail_sailbars_polar = Draft.make_polar_array(windsail_sailbar, number=4, angle=360.0, center=FreeCAD.Vector(0, 0, 0), use_link=True)
  windsail_sailbars_polar.AxisReference = windshaft_axis
  windsail_sailbars_polar.Label = "Windsail_Sailbars_PolarArray"

  windsail = doc.addObject("Part::Compound", "Windsail")
  windsail.Links = [windsail_stocks, windsail_sailbars_polar]

  return (windsail_mount, windsail)

tower = createTower(doc)
cap = createCap(doc)
tunnel = createServoTunnel(doc)

# Combine windmill components
windmill_solids = doc.addObject('Part::Compound', 'Windmill_Solids')
windmill_solids.Links = [tower, cap]

windmill = doc.addObject("Part::Cut", "Windmill")
windmill.Base = windmill_solids
windmill.Tool = tunnel

# Import STEP
if IMPORT_STEP:
  print('Importing PCB STEP file...')
  pcb_import_shape = Part.read('../hardware/exports/pcb.step')
  print("> Imported shape type:", pcb_import_shape.ShapeType)
  print("> Number of solids:", len(pcb_import_shape.Solids))
  pcb_import = doc.addObject("Part::Feature", "PCB_Import")
  pcb_import.Shape = pcb_import_shape
  pcb_import.setExpression('Placement.Rotation.Angle', f'90 deg')
  pcb_import.setExpression('Placement.Rotation.Axis', u'vector(1; 0; 0)')
  pcb_import.setExpression('Placement.Base.y', f'{Params.WINDSHAFT_TO_CAP_BASE_HOR} + ({Params.TOWER_TOP_WIDTH}/2 * tan(22.5 deg))')
  pcb_import.setExpression('Placement.Base.z', f'{Params.WINDSHAFT_TO_ROOF_TOP_VER} - {Params.TOTAL_HEIGHT} + {Params.OUTER_WALL_THICKNESS} + {Params.PCB_OUTLINE_TOLERANCE}')

# Build windsail
(windsail_mount, windsail) = createWindsail(doc)

# Save FreeCAD document
doc.RecomputesFrozen = False
doc.recompute()
doc.saveAs("exports/enclosure.FCStd")

def export_to_stl(obj, export_path):
    # High-definition mesh parameters
    linear_deflection = 0.01
    angular_deflection = math.radians(0.5)
    relative = False

    print(f'Building mesh from {obj.Name}...')
    mesh = MeshPart.meshFromShape(obj.Shape, linear_deflection, angular_deflection, relative)

    # Mesh must be a document object for export
    mesh_obj = doc.addObject('Mesh::Feature', f'{obj.Name}_Mesh')
    mesh_obj.Mesh = mesh
    doc.recompute()

    print(f'Exporting mesh to {export_path}...')
    Mesh.export([mesh_obj], export_path)

# Export STL
if EXPORT_STL:
  export_to_stl(windmill, 'exports/tower.stl')
  export_to_stl(windsail_mount, 'exports/windsail-mount.stl')
  export_to_stl(windsail, 'exports/windsail.stl')
