from build123d import *

outer_diameter = 80.0
wall_thickness = 5.0
height = 30.0
rib_thickness = 2.0
rib_height = 20.0
rib_count = 8
central_hole_diameter = 10.0
counterbore_diameter = 16.0
counterbore_depth = 5.0
chamfer_distance = 2.0

inner_radius = (outer_diameter / 2) - wall_thickness
outer_radius = outer_diameter / 2

solid_body = Cylinder(outer_radius, height) - Cylinder(inner_radius, height)

bottom_face = solid_body.faces().sort_by(Axis.Z)[0]
solid_body = chamfer(bottom_face.edges(), chamfer_distance)

rib = Pos(inner_radius + rib_thickness / 2, 0, height / 2) * Box(rib_thickness, rib_thickness, rib_height)
ribs = rib
for i in range(1, rib_count):
    angle = i * 360.0 / rib_count
    ribs = ribs + Rot(0, 0, angle) * rib

solid_body = solid_body + ribs

solid_body = solid_body - Cylinder(central_hole_diameter / 2, height * 2)
solid_body = solid_body - Pos(0, 0, height - counterbore_depth / 2) * Cylinder(counterbore_diameter / 2, counterbore_depth)

part = solid_body
part.name = "ribbed_cylinder_with_counterbore"
export_step(part, "output.step")