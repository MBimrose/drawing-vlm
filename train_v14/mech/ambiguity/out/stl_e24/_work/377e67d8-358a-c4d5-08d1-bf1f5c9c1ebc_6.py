from build123d import *

plate_length = 100.0
plate_width = 80.0
plate_thickness = 10.0
slot_width = 30.0
slot_length = 60.0
rib_height = 5.0
rib_thickness = 2.0
chamfer_distance = 1.0
mount_hole_diameter = 6.0
mount_hole_offset = 10.0

base = Box(plate_length, plate_width, plate_thickness)
slot = Box(slot_width, slot_length, plate_thickness)
base = base - slot

rib = Box(rib_thickness, plate_width, rib_height)
base = base + rib

hole_r = mount_hole_diameter / 2
hole_h = plate_thickness + 2
for x, y in [
    (-plate_length/2 + mount_hole_offset, -plate_width/2 + mount_hole_offset),
    ( plate_length/2 - mount_hole_offset, -plate_width/2 + mount_hole_offset),
    (-plate_length/2 + mount_hole_offset,  plate_width/2 - mount_hole_offset),
    ( plate_length/2 - mount_hole_offset,  plate_width/2 - mount_hole_offset)
]:
    base = base - Pos(x, y, 0) * Cylinder(hole_r, hole_h)

base = chamfer(base.edges().filter_by(Axis.Z), chamfer_distance)

part = base
part.name = "plate_with_slot_rib_holes"
export_step(part, "output.step")