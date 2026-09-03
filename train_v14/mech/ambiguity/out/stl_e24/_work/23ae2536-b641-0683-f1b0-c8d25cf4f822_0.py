from build123d import *

horizontal_leg_length = 80.0
vertical_leg_length = 60.0
thickness = 10.0
fillet_radius = 2.0
blind_hole_diameter = 6.0
blind_hole_depth = 30.0
through_hole_diameter = 5.0
through_hole_spacing = 20.0
through_hole_count = 3

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0,0), (horizontal_leg_length, 0), (horizontal_leg_length, thickness),
                     (thickness, thickness), (thickness, vertical_leg_length), (0, vertical_leg_length), close=True)
        make_face()
    extrude(amount=thickness)

solid_body = p.part
inner_edge = solid_body.edges().filter_by(Axis.Z).sort_by(Axis.X)[2]
solid_body = fillet([inner_edge], fillet_radius)

solid_body = solid_body - Pos(thickness/2, vertical_leg_length - blind_hole_depth/2, thickness/2) * Rot(90, 0, 0) * Cylinder(blind_hole_diameter/2, blind_hole_depth)

for i in range(through_hole_count):
    x = horizontal_leg_length/2 + (i - (through_hole_count-1)/2) * through_hole_spacing
    solid_body = solid_body - Pos(x, thickness/2, thickness) * Cylinder(through_hole_diameter/2, thickness)

part = solid_body
part.name = "L_Bracket"
export_step(part, "output.step")