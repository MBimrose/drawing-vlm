from build123d import *

long_leg_length = 80.0
short_leg_length = 30.0
thickness = 5.0
bracket_depth = 10.0
fillet_radius = 2.0
hole_diameter = 8.0
rib_width = 4.0
rib_height = 6.0
rib_offset = 2.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0, 0), (long_leg_length, 0), (long_leg_length, thickness),
                     (thickness, thickness), (thickness, short_leg_length),
                     (0, short_leg_length), close=True)
        make_face()
    extrude(amount=bracket_depth)

solid_body = p.part
solid_body = fillet(solid_body.edges(), fillet_radius)

hole_center_x = thickness / 2
hole_center_y = thickness / 2
solid_body = solid_body - Pos(hole_center_x, hole_center_y, 0) * Cylinder(hole_diameter / 2, bracket_depth * 2)

rib = Pos(rib_offset + rib_width / 2, rib_offset + rib_height / 2, bracket_depth / 2) * Box(rib_width, rib_height, bracket_depth)
solid_body = solid_body + rib

part = solid_body
part.name = "L_bracket"
export_step(part, "output.step")