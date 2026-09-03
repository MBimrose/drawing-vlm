from build123d import *

leg_length = 70.0
leg_width = 20.0
thickness = 10.0
hole_diameter = 6.0
hole_depth = 8.0
chamfer_size = 1.0
pocket_radius = 15.0
pocket_depth = 4.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0, 0), (leg_length, 0), (leg_length, leg_width),
                     (leg_width, leg_width), (leg_width, leg_length),
                     (0, leg_length), close=True)
        make_face()
    extrude(amount=thickness)

solid_body = p.part

# Recessed hole at inner corner (10, 10)
solid_body = solid_body - Pos(leg_width/2, leg_width/2, thickness - hole_depth/2) * Cylinder(hole_diameter/2, hole_depth)

# Chamfer all vertical edges
solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_size)

# Circular pocket cut from top face
solid_body = solid_body - Pos(leg_width/2, leg_width/2, thickness - pocket_depth/2) * Cylinder(pocket_radius, pocket_depth)

part = solid_body
part.name = "L_bracket"
export_step(part, "output.step")