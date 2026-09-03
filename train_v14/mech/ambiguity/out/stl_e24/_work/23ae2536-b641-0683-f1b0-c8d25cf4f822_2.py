from build123d import *

long_leg_length = 80.0
short_leg_length = 60.0
thickness = 10.0
depth = 10.0
inner_fillet_radius = 2.0
blind_hole_diameter = 6.0
blind_hole_depth = 30.0
through_hole_diameter = 5.0
through_hole_spacing = 20.0
through_hole_offset = 15.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0, 0), (long_leg_length, 0), (long_leg_length, thickness),
                     (thickness, thickness), (thickness, short_leg_length),
                     (0, short_leg_length), close=True)
        make_face()
    extrude(amount=depth)

solid_body = p.part

inner_edge = [e for e in solid_body.edges().filter_by(Axis.Z) if abs(e.center().X - thickness) < 0.1 and abs(e.center().Y - thickness) < 0.1][0]
solid_body = fillet([inner_edge], inner_fillet_radius)

solid_body = solid_body - Pos(thickness/2, short_leg_length - blind_hole_depth/2, depth/2) * Rot(90, 0, 0) * Cylinder(blind_hole_diameter/2, blind_hole_depth)

for i in range(3):
    x = thickness + through_hole_offset + i * through_hole_spacing
    solid_body = solid_body - Pos(x, thickness/2, depth) * Cylinder(through_hole_diameter/2, depth)

part = solid_body
part.name = "L_Bracket"
export_step(part, "output.step")