from build123d import *

base_length = 80.0
base_width = 50.0
base_thickness = 8.0
slot_length = 40.0
slot_width = 20.0
hole_diameter = 4.0
hole_spacing = 40.0
chamfer_distance = 1.0
rib_height = 2.0
rib_width = 6.0
rib_offset = 10.0

base = Box(base_length, base_width, base_thickness)
slot = Box(slot_width, slot_length, base_thickness)
base = base - slot

for x in [-hole_spacing/2, hole_spacing/2]:
    base = base - Pos(x, 0, 0) * Cylinder(hole_diameter/2, base_thickness)

base = chamfer(base.edges().filter_by(Axis.Z), chamfer_distance)

rib = Pos(-base_length/2 + rib_offset, 0, rib_height/2) * Box(rib_width, base_width - 2*rib_offset, rib_height)
part = base + rib
part.name = "base_with_slot_holes_and_rib"
export_step(part, "output.step")