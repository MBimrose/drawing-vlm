from build123d import *

bracket_length = 50.0
bracket_width = 30.0
bracket_thickness = 12.0
leg_thickness = 10.0
pocket_width = 6.0
pocket_length = 8.0
pocket_depth = 6.0
hole_diameter = 6.0
hole_depth = 8.0
chamfer_size = 0.2

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0, 0), (bracket_length, 0), (bracket_length, leg_thickness),
                     (leg_thickness, leg_thickness + 5), (leg_thickness, bracket_width),
                     (0, bracket_width), close=True)
        make_face()
    extrude(amount=bracket_thickness)

solid_body = p.part
solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_size)

# Pocket 1: center(25, 5, 12) -> offset(20, 0, 6)
solid_body = solid_body - Pos(20, 0, bracket_thickness - pocket_depth/2) * Box(pocket_width, pocket_length, pocket_depth)

# Pocket 2: center(5, 15, 12) -> offset(0, 10, 6)
solid_body = solid_body - Pos(0, 10, bracket_thickness - pocket_depth/2) * Box(pocket_width, pocket_length, pocket_depth)

# Hole: center(5, 25, 0) -> offset(0, 20, -4)
solid_body = solid_body - Pos(0, 20, hole_depth/2) * Cylinder(hole_diameter/2, hole_depth)

part = solid_body
part.name = "bracket"
export_step(part, "output.step")