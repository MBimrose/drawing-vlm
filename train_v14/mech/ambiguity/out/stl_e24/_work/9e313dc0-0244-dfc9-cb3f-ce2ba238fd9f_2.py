from build123d import *

outer_diameter = 80.0
height = 20.0
wall_thickness = 5.0
pocket_width = 12.0
pocket_depth = 6.0
pocket_height = 18.0
set_screw_diameter = 3.0
set_screw_offset = 0.0

outer_radius = outer_diameter / 2.0
inner_radius = outer_radius - wall_thickness

solid_body = Cylinder(outer_radius, height) - Cylinder(inner_radius, height)

pocket_box = Pos(outer_radius - pocket_depth/2, 0, 0) * Box(pocket_width, pocket_depth, pocket_height)
solid_body = solid_body - pocket_box

set_screw_cyl = Pos(outer_radius - wall_thickness/2, 0, 0) * Rot(0, 90, 0) * Cylinder(set_screw_diameter/2, wall_thickness + 2)
solid_body = solid_body - set_screw_cyl

part = solid_body
part.name = "hollow_cylinder_with_pocket_and_set_screw"
export_step(part, "output.step")