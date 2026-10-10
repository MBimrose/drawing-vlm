from build123d import *
import math

outer_diameter = 60.0
inner_diameter = 30.0
collar_length = 20.0
rib_width = 4.0
rib_height = 12.0
rib_depth = 6.0
rib_count = 4
chamfer_size = 1.0
outer_radius = outer_diameter / 2.0
inner_radius = inner_diameter / 2.0

solid_body = Cylinder(outer_radius, collar_length) - Cylinder(inner_radius, collar_length)

for i in range(rib_count):
    angle = i * 360.0 / rib_count
    rib = Rot(0, 0, angle) * Pos(outer_radius - rib_depth / 2.0, 0, 0) * Box(rib_depth, rib_width, rib_height)
    solid_body = solid_body - rib

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
top_edges = top_face.edges()
solid_body = chamfer(top_edges, chamfer_size)

part = solid_body
part.name = "collar_with_ribs"
export_step(part, "output.step")