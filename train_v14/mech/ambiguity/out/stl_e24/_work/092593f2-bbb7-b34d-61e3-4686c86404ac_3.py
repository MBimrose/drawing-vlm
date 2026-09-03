from build123d import *

bracket_length = 80.0
bracket_width = 40.0
bracket_thickness = 4.0
pocket_width = 20.0
pocket_length = 30.0
pocket_depth = 4.0
pocket_fillet_radius = 3.0
hole_diameter = 5.0
hole_spacing = 30.0
hole_edge_margin = 8.0
rib_height = 2.0
rib_width = 6.0

base = Box(bracket_length, bracket_width, bracket_thickness)

pocket_center_x = bracket_length / 2 - pocket_length / 2 - 5
pocket = Pos(pocket_center_x, 0, 0) * Box(pocket_width, pocket_length, pocket_depth)
pocket = fillet(pocket.edges().filter_by(Axis.Z), pocket_fillet_radius)

result = base - pocket

hole_center_x = -bracket_length / 2 + hole_edge_margin
for y in [-hole_spacing / 2, hole_spacing / 2]:
    result = result - Pos(hole_center_x, y, 0) * Cylinder(hole_diameter / 2, bracket_thickness)

rib = Pos(bracket_length / 2 + rib_width / 2, 0, 0) * Box(rib_width, bracket_width - 10, rib_height)
result = result + rib

part = result
part.name = "bracket"
export_step(part, "output.step")