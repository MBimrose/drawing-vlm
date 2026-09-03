from build123d import *

plate_length = 80.0
plate_width = 30.0
plate_thickness = 6.0
boss_radius = 12.0
boss_height = 5.0
slot_width = 6.0
slot_length = 20.0
hole_diameter = 4.0
hole_offset_x = 20.0
hole_offset_y = 6.0
rib_width = 4.0
rib_length = 20.0
rib_height = 2.0
chamfer_dist = 0.5

result = Pos(0, 0, plate_thickness/2) * Box(plate_length, plate_width, plate_thickness)
result = result + Pos(0, 0, plate_thickness + boss_height/2) * Cylinder(boss_radius, boss_height)

slot = Box(slot_width, slot_length, plate_thickness)
result = result - Pos(-plate_length/2 + slot_width/2, 0, plate_thickness/2) * slot
result = result - Pos(plate_length/2 - slot_width/2, 0, plate_thickness/2) * slot

hole = Cylinder(hole_diameter/2, plate_thickness + boss_height + 10)
for x, y in [(-hole_offset_x, -hole_offset_y), (-hole_offset_x, hole_offset_y),
             (hole_offset_x, -hole_offset_y), (hole_offset_x, hole_offset_y)]:
    result = result - Pos(x, y, plate_thickness/2) * hole

rib = Box(rib_width, rib_length, rib_height)
result = result + Pos(-plate_length/4, 0, rib_height/2) * rib
result = result + Pos(plate_length/4, 0, rib_height/2) * rib

top_face = result.faces().sort_by(Axis.Z)[-1]
result = chamfer(top_face.edges(), chamfer_dist)

part = result
part.name = "plate_with_boss_slots_holes_ribs"
export_step(part, "output.step")