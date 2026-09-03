from build123d import *

plate_length = 80.0
plate_width = 60.0
plate_thickness = 10.0
rib_width = 2.0
rib_height = 2.0
boss_diameter = 30.0
boss_height = 2.0
hole_diameter = 8.0
hole_depth = 3.0
hole_offset_x = 15.0
hole_offset_y = 10.0
chamfer_distance = 1.0

base = Box(plate_length, plate_width, plate_thickness)
base = chamfer(base.edges().filter_by(Axis.Z), chamfer_distance)

rib = Pos(0, 0, plate_thickness + rib_height/2) * Box(plate_length, plate_width, rib_height)
boss = Pos(0, 0, plate_thickness + rib_height + boss_height/2) * Cylinder(boss_diameter/2, boss_height)

result = base + rib + boss

hole_positions = [
    (hole_offset_x, hole_offset_y),
    (-hole_offset_x, hole_offset_y),
    (-hole_offset_x, -hole_offset_y),
    (hole_offset_x, -hole_offset_y)
]
for x, y in hole_positions:
    result = result - Pos(x, y, plate_thickness - hole_depth/2) * Cylinder(hole_diameter/2, hole_depth)

part = result
part.name = "plate_with_rib_boss_and_holes"
export_step(part, "output.step")