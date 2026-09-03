from build123d import *
import math

outer_diameter = 80.0
wall_thickness = 6.0
height = 60.0
rib_thickness = 2.0
rib_height = 12.0
rib_count = 12
chamfer_size = 1.5

outer_radius = outer_diameter / 2.0
inner_radius = outer_radius - wall_thickness
rib_radius = inner_radius - rib_thickness / 2.0

solid_body = Cylinder(outer_radius, height) - Cylinder(inner_radius, height)

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
top_edges = top_face.edges()
solid_body = chamfer(top_edges, chamfer_size)

for i in range(rib_count):
    angle = math.radians(i * 360.0 / rib_count)
    px = rib_radius * math.cos(angle)
    py = rib_radius * math.sin(angle)
    rib = Pos(px, py, height / 2.0) * Box(rib_thickness, rib_height, height)
    solid_body = solid_body + rib

part = solid_body
part.name = "XMountSocket"
export_step(part, "output.step")