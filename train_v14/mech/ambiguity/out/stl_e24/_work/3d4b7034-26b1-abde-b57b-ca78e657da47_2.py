from build123d import *

plate_length = 80.0
plate_width = 60.0
plate_thickness = 8.0
boss_diameter = 40.0
boss_height = 4.0
hole_diameter = 8.0
hole_offset_x = 20.0
hole_offset_y = 15.0
rib_width = 10.0
rib_height = 3.0
chamfer_distance = 1.0
pocket_length = 20.0
pocket_width = 10.0
pocket_depth = 4.0

base = Box(plate_length, plate_width, plate_thickness)
base = chamfer(base.edges().filter_by(Axis.Z), chamfer_distance)

boss = Pos(0, 0, plate_thickness) * Cylinder(boss_diameter / 2, boss_height)
rib = Pos(0, 0, plate_thickness) * Box(plate_length, rib_width, rib_height)

result = base + boss + rib

hole_positions = [
    (hole_offset_x, hole_offset_y),
    (-hole_offset_x, hole_offset_y),
    (hole_offset_x, -hole_offset_y),
    (-hole_offset_x, -hole_offset_y),
]
for x, y in hole_positions:
    result = result - Pos(x, y, plate_thickness / 2) * Cylinder(hole_diameter / 2, plate_thickness + boss_height + 10)

pocket = Pos(0, 0, plate_thickness + boss_height - pocket_depth / 2) * Box(pocket_length, pocket_width, pocket_depth)
result = result - pocket

part = result
part.name = "plate_with_boss_rib_holes_pocket"
export_step(part, "output.step")