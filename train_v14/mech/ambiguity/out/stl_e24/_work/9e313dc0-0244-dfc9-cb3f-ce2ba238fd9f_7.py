from build123d import *

outer_diameter = 80.0
wall_thickness = 5.0
length = 20.0
set_screw_diameter = 3.0
set_screw_depth = 12.0
pocket_width = 6.0
pocket_depth = 2.0
pocket_length = length * 0.9

outer_radius = outer_diameter / 2.0
inner_radius = outer_radius - wall_thickness

solid_body = Cylinder(outer_radius, length) - Cylinder(inner_radius, length)

pocket = Pos(outer_radius - pocket_depth/2, 0, 0) * Box(pocket_depth, pocket_width, pocket_length)
solid_body = solid_body - pocket

set_screw = Pos(outer_radius - set_screw_depth/2, 0, 0) * Rot(0, 90, 0) * Cylinder(set_screw_diameter/2, set_screw_depth)
solid_body = solid_body - set_screw

part = solid_body
part.name = "hollow_cylinder_with_pocket_and_setscrew"
export_step(part, "output.step")