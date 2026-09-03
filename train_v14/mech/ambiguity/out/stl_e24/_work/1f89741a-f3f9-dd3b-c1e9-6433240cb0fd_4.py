from build123d import *
import math

plate_length = 80.0
plate_width = 60.0
plate_thickness = 8.0
rib_height = 4.0
rib_width = 5.0
hole_diameter = 6.0
hole_spacing = 30.0
countersink_diameter = 12.0
countersink_angle = 82.0
fillet_radius = 1.0
boss_diameter = 15.0
boss_height = 4.0
slot_width = 20.0
slot_length = plate_length - 20.0
slot_depth = 2.0

with BuildPart() as p:
    with BuildSketch() as s:
        Rectangle(plate_length, plate_width)
    extrude(amount=plate_thickness)
    with BuildSketch(Plane.XY.offset(plate_thickness)) as s2:
        Rectangle(plate_length, plate_width)
    extrude(amount=rib_height)
    with BuildSketch(Plane.XY.offset(plate_thickness)) as s3:
        Rectangle(plate_length - 2*rib_width, plate_width - 2*rib_width)
    extrude(amount=rib_height, mode=Mode.SUBTRACT)
    with BuildSketch(Plane.XY.offset(plate_thickness)) as s4:
        Circle(boss_diameter/2)
    extrude(amount=boss_height)

solid_body = p.part

for x, y in [(-hole_spacing, 0), (0, 0), (hole_spacing, 0)]:
    solid_body = solid_body - Pos(x, y, 0) * Cylinder(hole_diameter/2, 100)

csk_depth = (countersink_diameter/2 - hole_diameter/2) / math.tan(math.radians(countersink_angle/2))
csk_cone = Pos(0, 0, plate_thickness + boss_height - csk_depth/2) * Cone(hole_diameter/2, countersink_diameter/2, csk_depth)
solid_body = solid_body - csk_cone

slot_cut = Pos(0, 0, plate_thickness + boss_height - slot_depth/2) * Box(slot_width, slot_length, slot_depth)
solid_body = solid_body - slot_cut

vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = fillet(vertical_edges, fillet_radius)

part = solid_body
part.name = "plate_with_rib_boss_and_holes"
export_step(part, "output.step")