from build123d import *
import math

outer_diameter = 70.0
wall_thickness = 5.0
length = 80.0
rib_count = 6
rib_thickness = 4.0
rib_height = wall_thickness
groove_width = 12.0
groove_depth = 2.0
groove_length = 8.0
chamfer_size = 2.0

outer_radius = outer_diameter / 2.0
inner_radius = outer_radius - wall_thickness

solid_body = Cylinder(outer_radius, length) - Cylinder(inner_radius, length)

rib = Pos(inner_radius + rib_height / 2.0, 0, 0) * Box(rib_thickness, rib_height, length)
ribs = rib
for i in range(1, rib_count):
    angle = 360.0 / rib_count * i
    ribs = ribs + Rot(0, 0, angle) * rib

solid_body = solid_body + ribs

groove = Pos(0, outer_radius - groove_depth / 2.0, 0) * Box(groove_width, groove_depth, groove_length)
solid_body = solid_body - groove

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
top_edges = top_face.edges()
solid_body = chamfer(top_edges, chamfer_size)

part = solid_body
part.name = "hollow_cylinder_with_ribs"
export_step(part, "output.step")