from build123d import *

outer_radius = 45.0
inner_radius = 30.0
length = 70.0
fillet_radius = 3.0
pocket_width = 20.0
pocket_length = 30.0
pocket_depth = 2.0
hole_diameter = 6.0
hole_spacing = 15.0
hole_rows = 2
hole_columns = 3
hole_offset_z = 10.0

solid_body = Cylinder(outer_radius, length) - Cylinder(inner_radius, length)
solid_body = fillet(solid_body.edges(), fillet_radius)

pocket_box = Pos(-inner_radius + pocket_depth/2, 0, 0) * Box(pocket_depth, pocket_width, pocket_length)
solid_body = solid_body - pocket_box

for i in range(hole_columns):
    for j in range(hole_rows):
        x = (i - (hole_columns-1)/2) * hole_spacing
        z = (j - (hole_rows-1)/2) * hole_spacing + hole_offset_z
        hole = Pos(x, 0, z) * Rot(90, 0, 0) * Cylinder(hole_diameter/2, length)
        solid_body = solid_body - hole

part = solid_body
part.name = "hollow_cylinder_with_pocket_and_holes"
export_step(part, "output.step")