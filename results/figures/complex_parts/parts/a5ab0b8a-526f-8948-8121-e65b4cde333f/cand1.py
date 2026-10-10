from build123d import *

plate_length = 80.0
plate_width = 60.0
plate_thickness = 6.0
boss_diameter = 20.0
boss_height = 30.0
hole_diameter = 12.0
hole_offset = 25.0
rib_width = 10.0
rib_height = 4.0
rib_offset = 20.0
chamfer_size = 0.8
pocket_length = 30.0
pocket_width = 20.0
pocket_depth = 4.0
pocket_offset_x = 15.0

base = Box(plate_length, plate_width, plate_thickness)
base = chamfer(base.edges().filter_by(Axis.Z), chamfer_size)

boss = Cylinder(boss_diameter / 2, boss_height)
result = base + boss

hole_positions = [
    (hole_offset, hole_offset),
    (-hole_offset, hole_offset),
    (-hole_offset, -hole_offset),
    (hole_offset, -hole_offset),
]
for x, y in hole_positions:
    result = result - Pos(x, y, 0) * Cylinder(hole_diameter / 2, 100)

rib1 = Pos(0, rib_offset, plate_thickness / 2 + rib_height / 2) * Box(plate_length, rib_width, rib_height)
rib2 = Pos(0, -rib_offset, plate_thickness / 2 + rib_height / 2) * Box(plate_length, rib_width, rib_height)
result = result + rib1 + rib2

pocket = Pos(pocket_offset_x, 0, plate_thickness / 2 + boss_height - pocket_depth / 2) * Box(pocket_length, pocket_width, pocket_depth)
result = result - pocket

part = result
part.name = "plate_with_boss_ribs_and_pocket"
export_step(part, "output.step")