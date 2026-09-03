from build123d import *

outer_radius = 30
inner_radius = 22
length = 30
wall_thickness = outer_radius - inner_radius
groove_width = 6
groove_depth = 4
groove_position = 15
pocket_width = 20
pocket_height = 10
pocket_depth = 6
pocket_offset = 5
rib_thickness = 2
rib_height = 5
rib_count = 4
rib_angle = 360 / rib_count
chamfer_size = 0.5

result = Cylinder(outer_radius, length) - Cylinder(inner_radius, length)

groove = Pos(0, groove_position, 0) * Cylinder(inner_radius - groove_depth, groove_width)
result = result - groove

pocket = Pos(0, inner_radius - pocket_offset, 0) * Box(pocket_width, pocket_height, pocket_depth)
result = result - pocket

for i in range(rib_count):
    angle = i * rib_angle
    rib = Rot(0, 0, angle) * Pos(outer_radius - rib_thickness/2, 0, 0) * Box(rib_thickness, rib_height, length)
    result = result + rib

part = result
part.name = "hollow_cylinder_with_groove_pocket_ribs"
export_step(part, "output.step")