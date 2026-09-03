from build123d import *

plate_length = 80.0
plate_width = 50.0
plate_thickness = 6.0
corner_radius = 4.0
chamfer_dist = 1.0
slot_length = 40.0
slot_width = 20.0
hole_diameter = 6.0
rib_slot_length = 12.0
rib_slot_width = 3.0
rib_offset = 20.0
rib_spacing = 15.0

solid = Box(plate_length, plate_width, plate_thickness)
solid = fillet(solid.edges().filter_by(Axis.Z), corner_radius)
solid = chamfer(solid.edges().filter_by(Axis.X), chamfer_dist)

solid = solid - Box(slot_length, slot_width, plate_thickness)

for x, y in [(-slot_length/2, 0), (slot_length/2, 0)]:
    solid = solid - Pos(x, y, 0) * Cylinder(hole_diameter/2, plate_thickness)

for x, y in [(-rib_offset, 0), (rib_offset, 0)]:
    solid = solid - Pos(x, y, 0) * Box(rib_slot_length, rib_slot_width, plate_thickness)

for x, y in [(-rib_spacing/2, 0), (rib_spacing/2, 0)]:
    solid = solid - Pos(x, y, 0) * Box(rib_slot_length, rib_slot_width, plate_thickness)

part = solid
part.name = "plate_with_slots_and_holes"
export_step(part, "output.step")