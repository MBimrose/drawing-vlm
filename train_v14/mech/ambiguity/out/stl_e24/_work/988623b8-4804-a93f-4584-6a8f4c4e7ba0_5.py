from build123d import *
import math

plate_width = 80.0
plate_height = 60.0
plate_thickness = 6.0
gusset_height = 20.0
gusset_width = 15.0
gusset_thickness = 4.0
mount_hole_diameter = 4.0
mount_hole_offset = 5.0
countersink_diameter = 5.0
countersink_angle = 82.0
countersink_depth = 3.0
slot_length = 12.0
slot_width = 4.0
slot_depth = 2.0
slot_spacing = 20.0

with BuildPart() as p:
    with BuildSketch() as s:
        Rectangle(plate_width, plate_height)
    extrude(amount=plate_thickness)

solid_body = p.part

corner_x = plate_width / 2 - mount_hole_offset
corner_y = plate_height / 2 - mount_hole_offset
for x, y in [(corner_x, corner_y), (-corner_x, corner_y), (-corner_x, -corner_y), (corner_x, -corner_y)]:
    solid_body = solid_body - Pos(x, y, plate_thickness/2) * Cylinder(mount_hole_diameter/2, plate_thickness + 1)

solid_body = solid_body - Pos(0, 0, plate_thickness/2) * Cylinder(countersink_diameter/2, plate_thickness + 1)

csk_radius = countersink_diameter / 2
csk_sink_radius = csk_radius + countersink_depth * math.tan(math.radians(countersink_angle / 2))
csk_cone = Pos(0, 0, plate_thickness - countersink_depth/2) * Cone(csk_radius, csk_sink_radius, countersink_depth)
solid_body = solid_body - csk_cone

num_slots = int((plate_width - 2 * mount_hole_offset) // slot_spacing) + 1
for i in range(num_slots):
    x = -plate_width / 2 + mount_hole_offset + i * slot_spacing
    solid_body = solid_body - Pos(x, 0, slot_depth/2) * Box(slot_length, slot_width, slot_depth)

with BuildPart() as g:
    with BuildSketch(Plane.YZ.offset(plate_width/2)) as gs:
        with BuildLine() as gl:
            Polyline((0, 0), (gusset_width, 0), (gusset_width/2, gusset_height), close=True)
        make_face()
    extrude(amount=gusset_thickness)

solid_body = solid_body + g.part

part = solid_body
part.name = "plate_with_gusset"
export_step(part, "output.step")