from build123d import *

leg_length = 80.0
leg_width = 20.0
thickness = 10.0
inner_fillet_radius = 15.0
hole_diameter = 5.0
hole_offset = 30.0
chamfer_distance = 1.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0, 0), (leg_length, 0), (leg_length, leg_width),
                     (leg_width, leg_width), (leg_width, leg_length),
                     (0, leg_length), close=True)
        make_face()
    extrude(amount=thickness)

solid_body = p.part

# Cut fillet circle at inner corner
solid_body = solid_body - Pos(leg_width, leg_width, thickness / 2) * Cylinder(inner_fillet_radius, thickness)

# Cut holes
solid_body = solid_body - Pos(hole_offset, leg_width / 2, thickness / 2) * Cylinder(hole_diameter / 2, thickness)
solid_body = solid_body - Pos(leg_width / 2, hole_offset, thickness / 2) * Cylinder(hole_diameter / 2, thickness)

# Chamfer all vertical edges
solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_distance)

part = solid_body
part.name = "L_bracket"
export_step(part, "output.step")