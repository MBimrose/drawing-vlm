from build123d import *

leg_length = 70.0
leg_width = 20.0
thickness = 10.0
inner_fillet_radius = 15.0
outer_chamfer = 1.0
hole_diameter = 5.0
hole_offset = 30.0

leg1 = Pos(leg_length/2, leg_width/2, thickness/2) * Box(leg_length, leg_width, thickness)
leg2 = Pos(leg_width/2, leg_length/2, thickness/2) * Box(leg_width, leg_length, thickness)
base = leg1 + leg2

inner_cut = Pos(leg_width, leg_width, thickness/2) * Cylinder(inner_fillet_radius, thickness)
result = base - inner_cut

result = chamfer(result.edges().filter_by(Axis.Z), outer_chamfer)

hole1 = Pos(hole_offset, leg_width/2, thickness/2) * Cylinder(hole_diameter/2, thickness)
hole2 = Pos(leg_width/2, hole_offset, thickness/2) * Cylinder(hole_diameter/2, thickness)
result = result - hole1 - hole2

part = result
part.name = "L_bracket"
export_step(part, "output.step")