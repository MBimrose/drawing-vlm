from build123d import *

vertical_leg_length = 70.0
horizontal_leg_length = 80.0
leg_thickness = 8.0
bracket_depth = 12.0
inner_fillet_radius = 3.0
hole_diameter = 6.0
hole_spacing = 20.0
hole_offset_from_bottom = 20.0
pocket_width = 20.0
pocket_depth = 6.0
pocket_offset_from_inner = 30.0

vertical = Pos(0, vertical_leg_length/2, 0) * Box(leg_thickness, vertical_leg_length, bracket_depth)
horizontal = Pos(leg_thickness/2 + horizontal_leg_length/2, leg_thickness/2, 0) * Box(horizontal_leg_length, leg_thickness, bracket_depth)
result = vertical + horizontal

inner_edge = result.edges().filter_by(Axis.Z).sort_by(Axis.X)[2]
result = fillet([inner_edge], inner_fillet_radius)

hole_positions = [
    (0, hole_offset_from_bottom),
    (0, hole_offset_from_bottom + hole_spacing),
    (0, hole_offset_from_bottom + 2 * hole_spacing)
]
for x, y in hole_positions:
    result = result - Pos(x, y, 0) * Cylinder(hole_diameter/2, bracket_depth * 2)

pocket = Pos(pocket_offset_from_inner, leg_thickness/2, bracket_depth/2) * Box(pocket_width, pocket_width, pocket_depth)
result = result - pocket

part = result
part.name = "L_bracket"
export_step(part, "output.step")