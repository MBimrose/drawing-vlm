from build123d import *

leg_length = 50.0
leg_width = 30.0
thickness = 10.0
extrude_depth = 12.0
relief_width = 6.0
relief_depth = 8.0
hole_diameter = 6.0
hole_depth = 8.0
chamfer_size = 1.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0,0), (leg_length,0), (leg_length,thickness), (thickness,thickness), (thickness,leg_width), (0,leg_width), close=True)
        make_face()
    extrude(amount=extrude_depth)
base = p.part

with BuildPart() as p2:
    with BuildSketch() as sk2:
        with BuildLine() as bl2:
            Polyline((thickness,thickness), (leg_length,thickness), (thickness,leg_width), close=True)
        make_face()
    extrude(amount=extrude_depth)
relief_cut = p2.part

result = base - relief_cut

pocket1 = Pos(leg_length/2, thickness/2, extrude_depth - relief_depth/2) * Box(relief_width, relief_depth, relief_depth)
result = result - pocket1

pocket2 = Pos(thickness/2, leg_width/2, extrude_depth - relief_depth/2) * Box(relief_width, relief_depth, relief_depth)
result = result - pocket2

hole = Pos(thickness/2, leg_width - thickness/2, hole_depth/2) * Cylinder(hole_diameter/2, hole_depth)
result = result - hole

part = result
part.name = "L_bracket_with_relief"
export_step(part, "output.step")