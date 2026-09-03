from build123d import *

plate_length = 80.0
plate_width = 60.0
plate_thickness = 8.0
boss_radius = 20.0
boss_height = 4.0
hole_diameter = 8.0
hole_offset_x = 20.0
hole_offset_y = 15.0
rib_width = 10.0
rib_height = 3.0
rib_length = plate_length - 2 * 5.0
pocket_length = 30.0
pocket_width = 20.0
pocket_depth = 2.0
chamfer_size = 1.0

result = Box(plate_length, plate_width, plate_thickness)
result = chamfer(result.edges().filter_by(Axis.Z), chamfer_size)
result = result + Pos(0, 0, plate_thickness) * Cylinder(boss_radius, boss_height)
result = result + Pos(0, 0, plate_thickness) * Box(rib_length, rib_width, rib_height)

hole_positions = [
    (hole_offset_x, hole_offset_y),
    (-hole_offset_x, hole_offset_y),
    (hole_offset_x, -hole_offset_y),
    (-hole_offset_x, -hole_offset_y),
]
for x, y in hole_positions:
    result = result - Pos(x, y, 0) * Cylinder(hole_diameter / 2, plate_thickness + boss_height + rib_height + 10)

result = result - Pos(0, 0, plate_thickness + boss_height - pocket_depth / 2) * Box(pocket_length, pocket_width, pocket_depth)

part = result
part.name = "plate_with_boss_rib_holes_pocket"
export_step(part, "output.step")