from build123d import *

outer_diameter = 80.0
wall_thickness = 5.0
height = 30.0
groove_width = 4.0
groove_depth = 2.0
groove_position = 10.0
tab_width = 20.0
tab_height = 10.0
tab_thickness = 6.0
tab_hole_diameter = 5.0
tab_hole_spacing = 14.0
chamfer_size = 0.8

outer_radius = outer_diameter / 2.0
inner_radius = outer_radius - wall_thickness

solid_body = Cylinder(outer_radius, height) - Cylinder(inner_radius, height)
solid_body = chamfer(solid_body.edges(), chamfer_size)

groove = Pos(0, 0, groove_position - groove_width / 2) * Cylinder(inner_radius + groove_depth, groove_width)
solid_body = solid_body - groove

tab = Pos(outer_radius + tab_thickness / 2 - 0.5, 0, 0) * Box(tab_thickness, tab_width, tab_height)
solid_body = solid_body + tab

hole1 = Pos(outer_radius + tab_thickness / 2, -tab_hole_spacing / 2, 0) * Rot(0, 90, 0) * Cylinder(tab_hole_diameter / 2, 200)
hole2 = Pos(outer_radius + tab_thickness / 2, tab_hole_spacing / 2, 0) * Rot(0, 90, 0) * Cylinder(tab_hole_diameter / 2, 200)
solid_body = solid_body - hole1 - hole2

part = solid_body
part.name = "hollow_cylinder_with_tab"
export_step(part, "output.step")