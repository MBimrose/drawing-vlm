from build123d import *
import math

outer_diameter = 80.0
wall_thickness = 6.0
height = 30.0
groove_width = 4.0
groove_depth = 2.0
groove_spacing = 8.0
groove_count = 3
chamfer_size = 1.0
hole_diameter = 4.0
hole_count = 6

outer_radius = outer_diameter / 2.0 + wall_thickness
inner_radius = outer_diameter / 2.0

solid_body = Pos(0, 0, height/2) * Cylinder(outer_radius, height)
solid_body = solid_body - Pos(0, 0, height/2) * Cylinder(inner_radius, height)

for i in range(groove_count):
    z_pos = height - groove_spacing * (i + 1) - groove_width / 2.0
    groove = Pos(0, 0, z_pos) * Cylinder(inner_radius - groove_depth, groove_width)
    solid_body = solid_body - groove

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
top_edges = top_face.edges()
solid_body = chamfer(top_edges, chamfer_size)

hole_radius = hole_diameter / 2.0
hole_r = outer_radius - wall_thickness / 2.0
for i in range(hole_count):
    angle = math.radians(i * 360.0 / hole_count)
    px = hole_r * math.cos(angle)
    py = hole_r * math.sin(angle)
    solid_body = solid_body - Pos(px, py, 0) * Cylinder(hole_radius, height + 2)

part = solid_body
part.name = "XMountSocket"
export_step(part, "output.step")