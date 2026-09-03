from build123d import *

outer_diameter = 60.0
inner_diameter = 30.0
length = 60.0
counterbore_diameter = 50.0
counterbore_depth = 15.0
fillet_radius = 2.0
mount_hole_diameter = 5.0
mount_hole_spacing = 40.0

outer_radius = outer_diameter / 2.0
inner_radius = inner_diameter / 2.0
counterbore_radius = counterbore_diameter / 2.0

solid_body = Pos(0, 0, length / 2) * Cylinder(outer_radius, length)
solid_body = solid_body - Pos(0, 0, length / 2) * Cylinder(inner_radius, length)
solid_body = solid_body - Pos(0, 0, length - counterbore_depth / 2) * Cylinder(counterbore_radius, counterbore_depth)
solid_body = fillet(solid_body.edges(), fillet_radius)

for x in [-mount_hole_spacing / 2, mount_hole_spacing / 2]:
    solid_body = solid_body - Pos(x, 0, length / 2) * Cylinder(mount_hole_diameter / 2, length)

part = solid_body
part.name = "cylindrical_part_with_counterbore"
export_step(part, "output.step")