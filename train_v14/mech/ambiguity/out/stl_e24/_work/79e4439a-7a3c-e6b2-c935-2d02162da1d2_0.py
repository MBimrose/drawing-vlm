from build123d import *
import math

outer_diameter = 80.0
height = 30.0
wall_thickness = 2.0
rib_count = 8
rib_width = 4.0
rib_height = 10.0
rib_thickness = 2.0
hole_diameter = 5.0
hole_count = 4
chamfer_size = 0.5

outer_radius = outer_diameter / 2.0
inner_radius = outer_radius - wall_thickness

solid_body = Cylinder(outer_radius, height)
top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[top_face])

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
top_edges = top_face.edges()
solid_body = chamfer(top_edges, chamfer_size)

rib = Box(rib_width, rib_height, rib_thickness)
rib = Pos(inner_radius - rib_width/2, 0, height/2 + rib_thickness/2) * rib

for i in range(rib_count):
    angle = i * 360.0 / rib_count
    rib_i = Rot(0, 0, angle) * rib
    solid_body = solid_body + rib_i

for i in range(hole_count):
    angle = i * 360.0 / hole_count
    rad = math.radians(angle)
    x = (outer_radius - wall_thickness/2) * math.cos(rad)
    y = (outer_radius - wall_thickness/2) * math.sin(rad)
    hole = Pos(x, y, height/2) * Rot(0, 90, angle) * Cylinder(hole_diameter/2, wall_thickness + 0.1)
    solid_body = solid_body - hole

part = solid_body
part.name = "hollow_cylinder_with_ribs_and_holes"
export_step(part, "output.step")