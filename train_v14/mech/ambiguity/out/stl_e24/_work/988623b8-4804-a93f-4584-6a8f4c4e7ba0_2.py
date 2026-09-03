from build123d import *
import math

plate_length = 80.0
plate_width = 60.0
plate_thickness = 6.0
gusset_width = 20.0
gusset_height = 30.0
gusset_thickness = 4.0
countersink_diameter = 5.0
countersink_angle = 82.0
mount_hole_diameter = 4.0
mount_hole_offset = 5.0
slot_length = 12.0
slot_width = 4.0
slot_depth = 2.0
slot_spacing = 15.0
num_slots = 4

base = Box(plate_length, plate_width, plate_thickness)

with BuildPart() as gp:
    with BuildSketch(Plane.YZ) as sk:
        with BuildLine() as bl:
            Polyline((0, 0), (gusset_width, 0), (gusset_width/2, gusset_height), close=True)
        make_face()
    extrude(amount=gusset_thickness)
gusset = Pos(plate_length/2 - gusset_thickness/2, 0, 0) * gp.part

result = base + gusset

csk_r = countersink_diameter / 2
csk_cr = csk_r + plate_thickness * math.tan(math.radians(countersink_angle / 2))
csk_hole = CounterSinkHole(csk_r, csk_cr, plate_thickness, countersink_angle)
result = result - Pos(0, 0, plate_thickness/2) * csk_hole

mount_points = [
    (-plate_length/2 + mount_hole_offset, -plate_width/2 + mount_hole_offset),
    ( plate_length/2 - mount_hole_offset, -plate_width/2 + mount_hole_offset),
    ( plate_length/2 - mount_hole_offset,  plate_width/2 - mount_hole_offset),
    (-plate_length/2 + mount_hole_offset,  plate_width/2 - mount_hole_offset)
]
for x, y in mount_points:
    result = result - Pos(x, y, 0) * Cylinder(mount_hole_diameter/2, plate_thickness)

slot_start_x = -plate_length/2 + slot_spacing/2
for i in range(num_slots):
    x = slot_start_x + i * slot_spacing
    result = result - Pos(x, 0, -plate_thickness/2 + slot_depth/2) * Box(slot_length, slot_width, slot_depth)

part = result
part.name = "plate_with_gusset"
export_step(part, "output.step")