from build123d import *
import math

plate_length = 80.0
plate_width = 60.0
plate_thickness = 6.0
gusset_height = 20.0
gusset_base = 30.0
gusset_thickness = 4.0
hole_diameter = 5.0
countersink_diameter = 10.0
countersink_angle = 82.0
mount_hole_diameter = 4.0
mount_hole_offset = 5.0
rib_width = 4.0
rib_length = 12.0
rib_depth = 2.0
rib_spacing = 20.0

with BuildPart() as p:
    with BuildSketch() as s:
        Rectangle(plate_length, plate_width)
    extrude(amount=plate_thickness)

solid_body = p.part

csk_depth = (countersink_diameter/2 - hole_diameter/2) / math.tan(math.radians(countersink_angle/2))
solid_body = solid_body - Pos(0, 0, plate_thickness/2) * Cylinder(hole_diameter/2, plate_thickness)
solid_body = solid_body - Pos(0, 0, plate_thickness - csk_depth/2) * Cone(hole_diameter/2, countersink_diameter/2, csk_depth)

corner_positions = [
    (-plate_length/2 + mount_hole_offset, -plate_width/2 + mount_hole_offset),
    (plate_length/2 - mount_hole_offset, -plate_width/2 + mount_hole_offset),
    (-plate_length/2 + mount_hole_offset, plate_width/2 - mount_hole_offset),
    (plate_length/2 - mount_hole_offset, plate_width/2 - mount_hole_offset),
]
for x, y in corner_positions:
    solid_body = solid_body - Pos(x, y, plate_thickness/2) * Cylinder(mount_hole_diameter/2, plate_thickness)

rib_count = int((plate_length - 2*mount_hole_offset) // rib_spacing) + 1
for i in range(rib_count):
    x_pos = -plate_length/2 + mount_hole_offset + i * rib_spacing
    solid_body = solid_body - Pos(x_pos, 0, rib_depth/2) * Box(rib_length, rib_width, rib_depth)

with BuildPart() as gp:
    with BuildSketch(Plane.YZ.offset(plate_length/2)) as gs:
        with BuildLine() as gl:
            Polyline((0, 0), (gusset_base/2, gusset_height), (-gusset_base/2, gusset_height), close=True)
        make_face()
    extrude(amount=gusset_thickness)

solid_body = solid_body + gp.part

part = solid_body
part.name = "plate_with_gusset"
export_step(part, "output.step")