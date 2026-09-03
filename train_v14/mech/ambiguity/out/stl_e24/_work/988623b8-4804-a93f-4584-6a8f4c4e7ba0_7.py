from build123d import *
import math

plate_length = 80.0
plate_width = 60.0
plate_thickness = 6.0
gusset_height = 20.0
gusset_width = 15.0
gusset_thickness = 4.0
countersink_diameter = 10.0
countersink_angle = 82.0
countersink_depth = (countersink_diameter/2) / math.tan(math.radians(countersink_angle/2))
mount_hole_diameter = 4.0
mount_hole_offset = 5.0
slot_length = 12.0
slot_width = 4.0
slot_spacing = 20.0
slot_depth = 2.0

solid_body = Box(plate_length, plate_width, plate_thickness)

for x, y in [(-plate_length/2 + mount_hole_offset, -plate_width/2 + mount_hole_offset),
             (plate_length/2 - mount_hole_offset, -plate_width/2 + mount_hole_offset),
             (plate_length/2 - mount_hole_offset, plate_width/2 - mount_hole_offset),
             (-plate_length/2 + mount_hole_offset, plate_width/2 - mount_hole_offset)]:
    solid_body = solid_body - Pos(x, y, 0) * Cylinder(mount_hole_diameter/2, plate_thickness)

solid_body = solid_body - Cylinder(5.0/2, plate_thickness)

csk_radius = countersink_diameter/2 + countersink_depth * math.tan(math.radians(countersink_angle/2))
solid_body = solid_body - Pos(0, 0, plate_thickness/2) * CounterSinkHole(countersink_diameter/2, csk_radius, countersink_depth, countersink_angle)

for i in range(4):
    x = (i - 1.5) * slot_spacing
    solid_body = solid_body - Pos(x, 0, -plate_thickness/2 + slot_depth/2) * Box(slot_length, slot_width, slot_depth)

with BuildPart() as gusset_bp:
    with BuildSketch(Plane.YZ) as sk:
        with BuildLine() as bl:
            l1 = Line((0, 0), (gusset_width, 0))
            l2 = Line(l1@1, (gusset_width/2, gusset_height))
            l3 = Line(l2@1, (0, 0))
        make_face()
    extrude(amount=gusset_thickness)

gusset = Pos(plate_length/2, -plate_width/2 + gusset_width/2, 0) * gusset_bp.part
solid_body = solid_body + gusset

part = solid_body
part.name = "plate_with_gusset"
export_step(part, "output.step")