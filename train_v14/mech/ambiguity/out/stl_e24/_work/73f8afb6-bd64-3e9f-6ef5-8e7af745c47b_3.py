from build123d import *

outer_diameter = 80.0
wall_thickness = 5.0
height = 30.0
groove_width = 6.0
groove_depth = 2.0
groove_position = 10.0
chamfer_size = 0.8
mount_hole_dia = 5.0
mount_hole_spacing = 14.0
tab_width = 20.0
tab_height = 10.0
tab_thickness = wall_thickness

outer_radius = outer_diameter / 2.0
inner_radius = outer_radius - wall_thickness

solid_body = Cylinder(outer_radius, height) - Cylinder(inner_radius, height)

groove = Pos(0, 0, groove_position - groove_width / 2.0) * Cylinder(inner_radius - groove_depth, groove_width)
solid_body = solid_body - groove

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = chamfer(top_face.edges(), chamfer_size)

bottom_face = solid_body.faces().sort_by(Axis.Z)[0]
solid_body = chamfer(bottom_face.edges(), chamfer_size)

tab = Pos(outer_radius + tab_thickness / 2.0 - 0.5, 0, 0) * Box(tab_thickness, tab_width, tab_height)
solid_body = solid_body + tab

for y in [-mount_hole_spacing / 2.0, mount_hole_spacing / 2.0]:
    hole = Pos(outer_radius + tab_thickness / 2.0, y, 0) * Rot(0, 90, 0) * Cylinder(mount_hole_dia / 2.0, 200)
    solid_body = solid_body - hole

part = solid_body
part.name = "hollow_cylinder_with_tab"
export_step(part, "output.step")