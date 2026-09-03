from build123d import *

bracket_length = 80.0
bracket_width = 50.0
bracket_thickness = 6.0
pocket_length = 30.0
pocket_width = 20.0
pocket_depth = 3.0
slot_length = 25.0
slot_width = 6.0
slot_offset_y = 20.0
mount_hole_diameter = 5.0
mount_hole_offset = 8.0
rib_thickness = 4.0
rib_width = 10.0

result = Box(bracket_length, bracket_width, bracket_thickness)

pocket = Pos(0, 0, bracket_thickness/2 - pocket_depth/2) * Box(pocket_length, pocket_width, pocket_depth)
result = result - pocket

slot1 = Pos(0, slot_offset_y, 0) * Box(slot_length, slot_width, bracket_thickness)
slot2 = Pos(0, -slot_offset_y, 0) * Box(slot_length, slot_width, bracket_thickness)
result = result - slot1 - slot2

hole_r = mount_hole_diameter / 2
for x in [-bracket_length/2 + mount_hole_offset, bracket_length/2 - mount_hole_offset]:
    for y in [-bracket_width/2 + mount_hole_offset, bracket_width/2 - mount_hole_offset]:
        result = result - Pos(x, y, 0) * Cylinder(hole_r, bracket_thickness)

rib1 = Pos(-bracket_length/2 + rib_thickness/2, 0, 0) * Box(rib_thickness, rib_width, bracket_thickness)
rib2 = Pos(bracket_length/2 - rib_thickness/2, 0, 0) * Box(rib_thickness, rib_width, bracket_thickness)
result = result + rib1 + rib2

part = result
part.name = "bracket_with_pocket_slots_ribs"
export_step(part, "output.step")