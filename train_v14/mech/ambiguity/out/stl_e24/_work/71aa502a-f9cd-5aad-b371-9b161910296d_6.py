from build123d import *

bracket_length = 80.0
bracket_width = 40.0
bracket_thickness = 8.0
rib_width = 6.0
mount_hole_diameter = 7.0
mount_hole_spacing = 60.0
blind_hole_diameter = 4.0
blind_hole_depth = 6.0
chamfer_size = 1.0
cbore_radius = 3.5
cbore_outer_radius = 5.0
cbore_depth = 2.0

base = Box(bracket_length, bracket_width, bracket_thickness)
rib = Pos(0, bracket_width/2 + rib_width/2, 0) * Box(bracket_length, rib_width, bracket_thickness)
solid_body = base + rib

for x in [-mount_hole_spacing/2, mount_hole_spacing/2]:
    solid_body = solid_body - Pos(x, 0, 0) * Cylinder(cbore_radius, bracket_thickness + 10)
    solid_body = solid_body - Pos(x, 0, bracket_thickness/2 - cbore_depth/2) * Cylinder(cbore_outer_radius, cbore_depth)

solid_body = solid_body - Pos(0, 0, bracket_thickness/2 - blind_hole_depth/2) * Cylinder(blind_hole_diameter/2, blind_hole_depth)

bottom_face = solid_body.faces().sort_by(Axis.Z)[0]
solid_body = chamfer(bottom_face.edges(), chamfer_size)

part = solid_body
part.name = "bracket"
export_step(part, "output.step")