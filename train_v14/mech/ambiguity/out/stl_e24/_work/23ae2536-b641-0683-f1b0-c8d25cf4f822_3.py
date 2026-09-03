from build123d import *

leg_length_vertical = 60.0
leg_length_horizontal = 80.0
thickness = 10.0
fillet_radius = 2.0
blind_hole_diameter = 6.0
blind_hole_depth = 30.0
through_hole_diameter = 5.0
through_hole_spacing = 20.0
through_hole_offset = 15.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0,0), (leg_length_horizontal, 0), (leg_length_horizontal, thickness),
                     (thickness, thickness), (thickness, leg_length_vertical), (0, leg_length_vertical), close=True)
        make_face()
    extrude(amount=thickness)

solid_body = p.part
inner_edges = [e for e in solid_body.edges().filter_by(Axis.Z) if abs(e.center().X - thickness) < 0.1 and abs(e.center().Y - thickness) < 0.1]
solid_body = fillet(inner_edges, fillet_radius)

solid_body = solid_body - Pos(thickness/2, leg_length_vertical - blind_hole_depth/2, thickness/2) * Rot(90, 0, 0) * Cylinder(blind_hole_diameter/2, blind_hole_depth)

for i in range(3):
    x = thickness + through_hole_offset + i * through_hole_spacing
    solid_body = solid_body - Pos(x, thickness/2, thickness) * Cylinder(through_hole_diameter/2, thickness)

part = solid_body
part.name = "L_Bracket"
export_step(part, "output.step")