from build123d import *

outer_radius = 30.0
inner_radius = 20.0
length = 50.0
groove_width = 6.0
groove_depth = 4.0
rib_width = 4.0
rib_height = 10.0
rib_count = 6
rib_overlap = 0.5

solid_body = Cylinder(outer_radius, length) - Cylinder(inner_radius, length)

groove_cyl = Cylinder(outer_radius - groove_depth, groove_width)
solid_body = solid_body - groove_cyl

rib_center_x = inner_radius + rib_height / 2.0 - rib_overlap
rib = Box(rib_height, rib_width, length)
ribs = Pos(rib_center_x, 0, length / 2) * rib
for i in range(1, rib_count):
    angle = i * 360.0 / rib_count
    ribs = ribs + Rot(0, 0, angle) * Pos(rib_center_x, 0, length / 2) * rib

solid_body = solid_body + ribs

part = solid_body
part.name = "hollow_cylinder_with_groove_and_ribs"
export_step(part, "output.step")