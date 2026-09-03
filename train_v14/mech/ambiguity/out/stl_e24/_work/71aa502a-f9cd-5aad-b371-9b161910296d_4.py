from build123d import *

bracket_length = 80.0
bracket_width = 40.0
bracket_thickness = 8.0
rib_height = 6.0
rib_thickness = 4.0
rib_offset_from_front = 5.0
hole_diameter = 7.0
hole_counterbore_diameter = 10.0
hole_counterbore_depth = 6.0
hole_offset_from_end = 10.0
blind_hole_diameter = 4.0
blind_hole_depth = 2.0
chamfer_size = 1.0

base = Box(bracket_length, bracket_width, bracket_thickness)
rib = Pos(0, bracket_width/2 + rib_height/2, 0) * Box(bracket_length, rib_height, bracket_thickness)
solid_body = base + rib

for x in [-bracket_length/2 + hole_offset_from_end, bracket_length/2 - hole_offset_from_end]:
    solid_body = solid_body - Pos(x, 0, bracket_thickness/2 - hole_counterbore_depth/2) * Cylinder(hole_counterbore_diameter/2, hole_counterbore_depth)
    solid_body = solid_body - Pos(x, 0, 0) * Cylinder(hole_diameter/2, bracket_thickness + 10)

solid_body = solid_body - Pos(0, 0, bracket_thickness/2 - blind_hole_depth/2) * Cylinder(blind_hole_diameter/2, blind_hole_depth)

bottom_face = solid_body.faces().sort_by(Axis.Z)[0]
solid_body = chamfer(bottom_face.edges(), chamfer_size)

part = solid_body
part.name = "bracket_with_rib_and_holes"
export_step(part, "output.step")