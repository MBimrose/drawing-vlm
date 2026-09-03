from build123d import *
import math

outer_diameter = 80.0
height = 30.0
wall_thickness = 2.0
rib_count = 8
rib_thickness = 4.0
rib_height = 10.0
chamfer_size = 0.5
hole_diameter = 5.0
hole_count = 4

outer_radius = outer_diameter / 2.0
inner_radius = outer_radius - wall_thickness

solid_body = Cylinder(outer_radius, height)
top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[top_face])

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
top_edges = top_face.edges()
solid_body = chamfer(top_edges, chamfer_size)

rib_center_x = inner_radius - rib_thickness / 2.0
rib_center_z = height / 2.0
for i in range(rib_count):
    angle = i * 360.0 / rib_count
    rib = Rot(0, 0, angle) * Pos(rib_center_x, 0, rib_center_z) * Box(rib_thickness, rib_height, wall_thickness)
    solid_body = solid_body + rib

hole_center_x = outer_radius - wall_thickness / 2.0
hole_center_z = height / 2.0
for i in range(hole_count):
    angle = i * 360.0 / hole_count
    hole = Rot(0, 0, angle) * Pos(hole_center_x, 0, hole_center_z) * Rot(0, 90, 0) * Cylinder(hole_diameter / 2.0, wall_thickness + 0.1)
    solid_body = solid_body - hole

part = solid_body
part.name = "ribbed_cup_with_holes"
export_step(part, "output.step")