from build123d import *

plate_length = 100.0
plate_width = 80.0
plate_thickness = 6.0
flange_width = 10.0
flange_thickness = plate_thickness
chamfer_size = 1.0
boss_size = 30.0
boss_height = 4.0
hole_diameter = 6.0
hole_depth = 4.0
hole_spacing = 12.0
rib_width = 8.0
rib_height = 2.0
rib_spacing = 20.0
slot_length = 40.0
slot_width = 20.0

result = Box(plate_length, plate_width, plate_thickness)
result = result + Pos(plate_length/2 + flange_width/2, 0, 0) * Box(flange_width, plate_width, flange_thickness)
result = chamfer(result.edges().filter_by(Axis.Z), chamfer_size)
result = result + Pos(plate_length/4, 0, plate_thickness/2 + boss_height/2) * Box(boss_size, boss_size, boss_height)

hole_positions = [
    (-hole_spacing/2, -hole_spacing/2),
    (hole_spacing/2, -hole_spacing/2),
    (-hole_spacing/2, hole_spacing/2),
    (hole_spacing/2, hole_spacing/2),
]
for dx, dy in hole_positions:
    result = result - Pos(plate_length/4 + dx, dy, plate_thickness/2 + boss_height - hole_depth/2) * Cylinder(hole_diameter/2, hole_depth)

num_ribs = int((plate_length - 2*flange_width) // rib_spacing)
for i in range(num_ribs):
    x_pos = -plate_length/2 + flange_width + rib_spacing/2 + i * rib_spacing
    result = result + Pos(x_pos, 0, -plate_thickness/2 + rib_height/2) * Box(rib_width, plate_width - 2*flange_width, rib_height)

result = result - Pos(-plate_length/4, 0, 0) * Box(slot_length, slot_width, plate_thickness)

part = result
part.name = "plate_with_flange_boss_ribs"
export_step(part, "output.step")