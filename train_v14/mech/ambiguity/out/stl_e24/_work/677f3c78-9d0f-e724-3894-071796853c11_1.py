from build123d import *

leg_length = 70.0
leg_width = 20.0
thickness = 10.0
inner_fillet_radius = 15.0
outer_chamfer = 1.0
hole_diameter = 5.0
hole_spacing = 30.0
hole_offset = 20.0

vertical = Pos(leg_width/2, leg_length/2, thickness/2) * Box(leg_width, leg_length, thickness)
horizontal = Pos(leg_length/2, leg_width/2, thickness/2) * Box(leg_length, leg_width, thickness)
base = vertical + horizontal

inner_cut = Pos(leg_width, leg_width, thickness/2) * Cylinder(inner_fillet_radius, thickness)
result = base - inner_cut

result = chamfer(result.edges().filter_by(Axis.Z), outer_chamfer)

for x, y in [(leg_width/2, hole_offset), (leg_width/2, hole_offset + hole_spacing)]:
    result = result - Pos(x, y, thickness/2) * Cylinder(hole_diameter/2, thickness)

for x, y in [(hole_offset, leg_width/2), (hole_offset + hole_spacing, leg_width/2)]:
    result = result - Pos(x, y, thickness/2) * Cylinder(hole_diameter/2, thickness)

part = result
part.name = "L_bracket"
export_step(part, "output.step")