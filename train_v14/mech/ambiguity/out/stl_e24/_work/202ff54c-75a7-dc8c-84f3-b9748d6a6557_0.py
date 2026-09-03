from build123d import *
import math

outer_diameter = 80.0
inner_diameter = 40.0
length = 60.0
wall_thickness = (outer_diameter - inner_diameter) / 2.0
pocket_width = 12.0
pocket_depth = wall_thickness * 0.9
pocket_length = 20.0
chamfer_size = 3.0
mount_hole_dia = 4.0
mount_hole_offset = 15.0
rib_thickness = 3.0
rib_height = 6.0
rib_length = 30.0
rib_count = 4

outer_radius = outer_diameter / 2.0
inner_radius = inner_diameter / 2.0

solid_body = Cylinder(outer_radius, length) - Cylinder(inner_radius, length)

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = chamfer(top_face.edges(), chamfer_size)

pocket = Pos(outer_radius - pocket_depth / 2.0, 0, 0) * Box(pocket_depth, pocket_width, pocket_length)
solid_body = solid_body - pocket

for x, y in [(mount_hole_offset, 0), (-mount_hole_offset, 0)]:
    solid_body = solid_body - Pos(x, y, 0) * Cylinder(mount_hole_dia / 2, length)

for i in range(rib_count):
    angle = i * 360.0 / rib_count
    rib = Rot(0, 0, angle) * Pos(outer_radius, 0, 0) * Box(rib_thickness, rib_height, rib_length)
    solid_body = solid_body + rib

part = solid_body
part.name = "hollow_cylinder_with_pocket_and_ribs"
export_step(part, "output.step")