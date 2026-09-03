from build123d import *

plate_width = 80.0
plate_depth = 30.0
plate_thickness = 6.0
boss_radius = 12.0
boss_height = 5.0
slot_width = 8.0
slot_length = 20.0
hole_diameter = 4.0
hole_spacing_x = 40.0
hole_spacing_y = 12.0
chamfer_size = 0.5
rib_width = 4.0
rib_height = 2.0

result = Box(plate_width, plate_depth, plate_thickness)
result = result + Pos(0, 0, plate_thickness/2 + boss_height/2) * Cylinder(boss_radius, boss_height)

slot_x = plate_width/2 - slot_width/2
result = result - Pos(-slot_x, 0, 0) * Box(slot_width, slot_length, plate_thickness)
result = result - Pos(slot_x, 0, 0) * Box(slot_width, slot_length, plate_thickness)

hole_positions = [
    (-hole_spacing_x/2, -hole_spacing_y/2),
    (hole_spacing_x/2, -hole_spacing_y/2),
    (-hole_spacing_x/2, hole_spacing_y/2),
    (hole_spacing_x/2, hole_spacing_y/2),
]
for x, y in hole_positions:
    result = result - Pos(x, y, 0) * Cylinder(hole_diameter/2, plate_thickness)

rib_x = plate_width/2 - rib_width/2 - 5
result = result + Pos(-rib_x, 0, -plate_thickness/2 + rib_height/2) * Box(rib_width, plate_depth - 10, rib_height)
result = result + Pos(rib_x, 0, -plate_thickness/2 + rib_height/2) * Box(rib_width, plate_depth - 10, rib_height)

top_face = result.faces().sort_by(Axis.Z)[-1]
result = chamfer(top_face.edges(), chamfer_size)

part = result
part.name = "plate_with_boss_slots_holes_ribs"
export_step(part, "output.step")