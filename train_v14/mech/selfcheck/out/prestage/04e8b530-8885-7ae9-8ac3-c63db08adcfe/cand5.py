from build123d import *
import math

outer_diameter = 80.0
height = 30.0
wall_thickness = 5.0
fillet_radius = 2.0
central_hole_diameter = 10.0
rib_count = 8
rib_thickness = 2.0
rib_width = 3.0
rib_height = height - 2 * wall_thickness

outer_radius = outer_diameter / 2.0
inner_radius = outer_radius - wall_thickness

solid_body = Cylinder(outer_radius, height)
top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[top_face])
solid_body = fillet(solid_body.edges(), fillet_radius)
solid_body = solid_body - Cylinder(central_hole_diameter / 2, height)

rib = Pos(inner_radius - rib_thickness / 2.0, 0, wall_thickness + rib_height / 2.0) * Box(rib_thickness, rib_width, rib_height)
ribs = rib
for i in range(1, rib_count):
    angle = i * 360.0 / rib_count
    ribs = ribs + Rot(0, 0, angle) * rib

part = solid_body + ribs
part.name = "hollow_cylinder_with_ribs"
export_step(part, "output.step")