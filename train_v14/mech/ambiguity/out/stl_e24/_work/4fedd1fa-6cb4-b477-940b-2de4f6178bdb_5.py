from build123d import *

plate_width = 60
plate_depth = 60
plate_thickness = 8
rib_width = 8
rib_height = 6
rib_thickness = 4
slot_length = 30
slot_width = 10
hole_diameter = 10
chamfer_size = 2

base = Box(plate_width, plate_depth, plate_thickness)
base = chamfer(base.edges().filter_by(Axis.Z), chamfer_size)

rib = Box(rib_width, rib_height, rib_thickness)
rib_left = Pos(-plate_width/2 - rib_width/2, 0, 0) * rib
rib_right = Pos(plate_width/2 + rib_width/2, 0, 0) * rib

combined = base + rib_left + rib_right

slot = Box(slot_length, slot_width, plate_thickness + 2)
combined = combined - slot

hole = Cylinder(hole_diameter/2, plate_thickness + 2)
combined = combined - hole

part = combined
part.name = "plate_with_ribs_slot_and_hole"
export_step(part, "output.step")