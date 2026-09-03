from build123d import *

outer_diameter = 80.0
wall_thickness = 5.0
height = 20.0
pocket_width = 12.0
pocket_height = 6.0
pocket_depth = 3.0
set_screw_diameter = 3.0

outer_radius = outer_diameter / 2.0
inner_radius = outer_radius - wall_thickness

solid_body = Cylinder(outer_radius, height) - Cylinder(inner_radius, height)

pocket = Pos(outer_radius - pocket_depth/2, 0, 0) * Box(pocket_width, pocket_height, pocket_depth)
solid_body = solid_body - pocket

hole = Pos(outer_radius - wall_thickness/2, 0, 0) * Rot(0, 90, 0) * Cylinder(set_screw_diameter/2, wall_thickness + 1)
solid_body = solid_body - hole

part = solid_body
part.name = "hollow_cylinder_with_pocket_and_hole"
export_step(part, "output.step")