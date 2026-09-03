from build123d import *

bracket_length = 80.0
bracket_width = 40.0
bracket_thickness = 8.0
rib_width = 6.0
rib_height = 4.0
hole_diameter = 7.0
hole_offset_from_end = 10.0
chamfer_distance = 1.0
counterbore_diameter = 10.0
counterbore_depth = 2.0
blind_hole_diameter = 4.0
blind_hole_depth = 2.0

base = Pos(0, 0, bracket_thickness/2) * Box(bracket_length, bracket_width, bracket_thickness)
rib = Pos(0, bracket_width/2 + rib_width/2, bracket_thickness/2) * Box(bracket_length, rib_width, rib_height)
solid = base + rib

hole_x1 = -bracket_length/2 + hole_offset_from_end
hole_x2 = bracket_length/2 - hole_offset_from_end
hole_positions = [(hole_x1, 0), (hole_x2, 0)]

for x, y in hole_positions:
    solid = solid - Pos(x, y, bracket_thickness - counterbore_depth/2) * Cylinder(counterbore_diameter/2, counterbore_depth)
    solid = solid - Pos(x, y, bracket_thickness/2) * Cylinder(hole_diameter/2, bracket_thickness + 10)

solid = solid - Pos(0, 0, bracket_thickness - blind_hole_depth/2) * Cylinder(blind_hole_diameter/2, blind_hole_depth)

bottom_face = solid.faces().sort_by(Axis.Z)[0]
solid = chamfer(bottom_face.edges(), chamfer_distance)

part = solid
part.name = "bracket_with_rib_and_holes"
export_step(part, "output.step")