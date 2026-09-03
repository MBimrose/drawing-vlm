from build123d import *

bracket_length = 80.0
bracket_width = 40.0
bracket_thickness = 6.0
rib_width = 6.0
rib_height = 3.0
rib_offset_from_edge = 5.0
hole_diameter = 5.0
hole_offset_from_end = 15.0
pocket_radius = 8.0
pocket_depth = 4.0
chamfer_size = 0.5

base = Box(bracket_length, bracket_width, bracket_thickness)
base = chamfer(base.edges().filter_by(Axis.Z), chamfer_size)

rib_center_y = -bracket_width/2 + rib_offset_from_edge + rib_width/2
rib = Pos(0, rib_center_y, bracket_thickness/2 + rib_height/2) * Box(rib_width, bracket_length - 2*rib_offset_from_edge, rib_height)

result = base + rib

hole_positions = [(-bracket_length/2 + hole_offset_from_end, 0), (bracket_length/2 - hole_offset_from_end, 0)]
for x, y in hole_positions:
    result = result - Pos(x, y, 0) * Cylinder(hole_diameter/2, bracket_thickness + rib_height + 10)

pocket_center_x = 0
pocket_center_y = bracket_width/2 - pocket_depth/2
pocket = Pos(pocket_center_x, pocket_center_y, 0) * Cylinder(pocket_radius, pocket_depth)
result = result - pocket

part = result
part.name = "bracket_with_rib"
export_step(part, "output.step")