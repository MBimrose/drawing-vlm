from build123d import *

leg_length = 50.0
leg_width = 30.0
thickness = 10.0
extrude_depth = 12.0
relief_factor = 0.2
hole_diameter = 6.0
hole_depth = 8.0
pocket_width = 6.0
pocket_height = 8.0
pocket_depth = 6.0
pocket_offset = 5.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0, 0), (leg_length, 0), (leg_length, thickness),
                     (thickness, thickness * (1 - relief_factor)),
                     (thickness, leg_width), (0, leg_width), close=True)
        make_face()
    extrude(amount=extrude_depth)

solid_body = p.part

# Hole on vertical leg (face <X), offset from center
solid_body = solid_body - Pos(thickness/2, leg_width - hole_depth/2, extrude_depth/2) * Cylinder(hole_diameter/2, hole_depth)

# Pocket on horizontal leg (face <Y), offset from center
solid_body = solid_body - Pos(leg_length/2, pocket_depth/2, extrude_depth/2) * Box(pocket_width, pocket_depth, pocket_height)

# Pocket on vertical leg (face <X), offset from center
solid_body = solid_body - Pos(pocket_depth/2, leg_width/2, extrude_depth/2) * Box(pocket_depth, pocket_width, pocket_height)

part = solid_body
part.name = "L_bracket_with_relief"
export_step(part, "output.step")