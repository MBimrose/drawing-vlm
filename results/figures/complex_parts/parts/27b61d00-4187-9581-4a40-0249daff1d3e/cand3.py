from build123d import *
import math

outer_diameter = 80.0
wall_thickness = 6.0
height = 50.0
rib_thickness = 4.0
rib_width = 12.0
rib_count = 12
central_hole_diameter = 20.0
counterbore_diameter = 30.0
counterbore_depth = 10.0
chamfer_size = 2.0

outer_radius = outer_diameter / 2.0
inner_radius = outer_radius - wall_thickness

solid_body = Cylinder(outer_radius, height)
top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[top_face])

top_edges = solid_body.edges().sort_by(Axis.Z)[-2:]
solid_body = chamfer(top_edges, chamfer_size)

solid_body = solid_body - Cylinder(central_hole_diameter / 2, height)
solid_body = solid_body - Pos(0, 0, height - counterbore_depth / 2) * Cylinder(counterbore_diameter / 2, counterbore_depth)

rib = Pos(inner_radius - rib_thickness / 2.0, 0, height / 2.0) * Box(rib_thickness, rib_width, height)
ribs = rib
for i in range(1, rib_count):
    angle = i * 360.0 / rib_count
    ribs = ribs + Rot(0, 0, angle) * rib

solid_body = solid_body + ribs

part = solid_body
part.name = "ribbed_shell_with_counterbore"
export_step(part, "output.step")