from build123d import *

plate_length = 80.0
plate_width = 60.0
plate_thickness = 8.0
rib_height = 3.0
rib_width = 10.0
boss_diameter = 40.0
boss_height = 6.0
hole_diameter = 8.0
hole_offset_x = 20.0
hole_offset_y = 15.0
chamfer_size = 1.0
pocket_width = 30.0
pocket_depth = 4.0

solid_body = Box(plate_length, plate_width, plate_thickness)
solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_size)

rib = Pos(0, 0, plate_thickness) * Box(plate_length, rib_width, rib_height)
solid_body = solid_body + rib

boss = Pos(0, 0, plate_thickness) * Cylinder(boss_diameter / 2, boss_height)
solid_body = solid_body + boss

hole_positions = [
    (hole_offset_x, hole_offset_y),
    (-hole_offset_x, hole_offset_y),
    (hole_offset_x, -hole_offset_y),
    (-hole_offset_x, -hole_offset_y),
]
for x, y in hole_positions:
    solid_body = solid_body - Pos(x, y, 0) * Cylinder(hole_diameter / 2, plate_thickness + boss_height + 10)

pocket = Pos(0, 0, plate_thickness + boss_height - pocket_depth / 2) * Box(pocket_width, pocket_width, pocket_depth)
solid_body = solid_body - pocket

part = solid_body
part.name = "plate_with_rib_boss_holes_pocket"
export_step(part, "output.step")