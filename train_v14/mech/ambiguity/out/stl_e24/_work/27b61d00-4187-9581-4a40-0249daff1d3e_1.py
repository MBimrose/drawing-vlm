from build123d import *
import math

outer_diameter = 80.0
height = 60.0
wall_thickness = 6.0
rib_count = 12
rib_thickness = 2.0
rib_height = 12.0
rib_length = 30.0
central_hole_diameter = 12.0
seat_diameter = 20.0
seat_depth = 5.0
chamfer_size = 2.0

outer_radius = outer_diameter / 2.0
inner_radius = outer_radius - wall_thickness

solid_body = Cylinder(outer_radius, height)
top_face = solid_body.faces().sort_by(Axis.Z)[-1]
bottom_face = solid_body.faces().sort_by(Axis.Z)[0]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[top_face, bottom_face])

solid_body = solid_body - Cylinder(central_hole_diameter / 2, height)

cone = Pos(0, 0, height - seat_depth) * Cone(seat_diameter / 2, 0, seat_depth)
solid_body = solid_body - cone

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
top_edges = top_face.edges()
solid_body = chamfer(top_edges, chamfer_size)

rib = Pos(inner_radius - rib_thickness / 2, 0, height / 2) * Box(rib_thickness, rib_height, rib_length)
ribs = rib
for i in range(1, rib_count):
    angle = i * 360.0 / rib_count
    ribs = ribs + Rot(0, 0, angle) * rib

solid_body = solid_body + ribs

part = solid_body
part.name = "hollow_cylinder_with_ribs"
export_step(part, "output.step")