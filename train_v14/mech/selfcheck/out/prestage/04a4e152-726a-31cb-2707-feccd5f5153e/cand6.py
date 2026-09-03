from build123d import *

leg_length = 50.0
leg_width = 30.0
thickness = 10.0
extrude_depth = 12.0
hole_diameter = 6.0
hole_depth = 8.0
pocket_width = 6.0
pocket_height = 8.0
pocket_depth = 6.0
pocket_offset = 5.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0,0), (leg_length,0), (leg_length,thickness), (thickness,thickness), (thickness,leg_width), (0,leg_width), close=True)
        make_face()
    extrude(amount=extrude_depth)

solid = p.part
solid = solid - Pos(leg_length/2, thickness/2, extrude_depth - pocket_depth/2) * Box(pocket_width, pocket_height, pocket_depth)
solid = solid - Pos(thickness/2, leg_width - pocket_offset, hole_depth/2) * Cylinder(hole_diameter/2, hole_depth)

part = solid
part.name = "L_bracket_with_pocket_and_hole"
export_step(part, "output.step")