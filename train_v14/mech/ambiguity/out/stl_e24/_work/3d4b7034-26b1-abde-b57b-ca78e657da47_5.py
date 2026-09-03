from build123d import *

plate_length = 80.0
plate_width = 60.0
plate_thickness = 8.0
boss_radius = 20.0
boss_height = 4.0
hole_diameter = 8.0
hole_offset_x = 20.0
hole_offset_y = 15.0
chamfer_size = 1.0
rib_height = 3.0
rib_width = 10.0
pocket_length = 30.0
pocket_width = 20.0
pocket_depth = 2.0

solid_body = Box(plate_length, plate_width, plate_thickness)
solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_size)

boss = Pos(0, 0, plate_thickness) * Cylinder(boss_radius, boss_height)
solid_body = solid_body + boss

rib = Pos(0, 0, plate_thickness) * Box(plate_length - 2 * rib_width, rib_width, rib_height)
solid_body = solid_body + rib

pocket = Pos(0, 0, plate_thickness + boss_height - pocket_depth / 2) * Box(pocket_length, pocket_width, pocket_depth)
solid_body = solid_body - pocket

hole_positions = [
    (hole_offset_x, hole_offset_y),
    (-hole_offset_x, hole_offset_y),
    (-hole_offset_x, -hole_offset_y),
    (hole_offset_x, -hole_offset_y),
]
for x, y in hole_positions:
    hole = Pos(x, y, 0) * Cylinder(hole_diameter / 2, plate_thickness + boss_height + 20)
    solid_body = solid_body - hole

part = solid_body
part.name = "plate_with_boss_rib_pocket_holes"
export_step(part, "output.step")