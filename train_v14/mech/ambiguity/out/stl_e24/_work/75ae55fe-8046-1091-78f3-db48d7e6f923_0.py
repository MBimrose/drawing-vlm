from build123d import *

bracket_length = 80.0
bracket_width = 25.0
bracket_thickness = 8.0
rib_height = 6.0
rib_width = 4.0
rib_spacing = 10.0
rib_thickness = 3.0
pocket_width = 30.0
pocket_depth = 12.0
hole_diameter = 5.0
hole_offset = 8.0
fillet_radius = 2.0

solid_body = Box(bracket_length, bracket_thickness, bracket_width)
solid_body = fillet(solid_body.edges().filter_by(Axis.Z), fillet_radius)

rib_count = int((bracket_length - 2 * hole_offset) // rib_spacing) + 1
for i in range(rib_count):
    x_pos = -bracket_length / 2 + hole_offset + i * rib_spacing
    rib = Pos(x_pos, bracket_thickness / 2 + rib_height / 2, rib_thickness / 2) * Box(rib_width, rib_height, rib_thickness)
    solid_body = solid_body + rib

pocket = Pos(0, 0, -bracket_width / 2 + pocket_depth / 2) * Box(pocket_width, pocket_depth, pocket_depth)
solid_body = solid_body - pocket

hole_positions = [
    (-bracket_length / 2 + hole_offset, -bracket_width / 2 + hole_offset),
    (bracket_length / 2 - hole_offset, -bracket_width / 2 + hole_offset),
    (-bracket_length / 2 + hole_offset, bracket_width / 2 - hole_offset),
    (bracket_length / 2 - hole_offset, bracket_width / 2 - hole_offset),
]
for x, z in hole_positions:
    hole = Pos(x, 0, z) * Rot(90, 0, 0) * Cylinder(hole_diameter / 2, bracket_thickness + 10)
    solid_body = solid_body - hole

part = solid_body
part.name = "bracket_with_ribs_pocket_holes"
export_step(part, "output.step")