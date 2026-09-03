from build123d import *
import math

outer_diameter = 80.0
height = 30.0
wall_thickness = 5.0
fillet_radius = 2.0
rib_count = 8
rib_thickness = 2.0
rib_width = 3.0
rib_height = height - 2 * wall_thickness
hole_diameter = 4.0

solid_body = Cylinder(outer_diameter / 2, height)
top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[top_face])
solid_body = fillet(solid_body.edges(), fillet_radius)

inner_radius = (outer_diameter / 2) - wall_thickness
rib_center_x = inner_radius - rib_thickness / 2
rib_center_z = wall_thickness + rib_height / 2

for i in range(rib_count):
    angle = i * 360.0 / rib_count
    rib = Rot(0, 0, angle) * Pos(rib_center_x, 0, rib_center_z) * Box(rib_thickness, rib_width, rib_height)
    solid_body = solid_body + rib

solid_body = solid_body - Cylinder(hole_diameter / 2, height * 2)

part = solid_body
part.name = "hollow_cylinder_with_ribs"
export_step(part, "output.step")