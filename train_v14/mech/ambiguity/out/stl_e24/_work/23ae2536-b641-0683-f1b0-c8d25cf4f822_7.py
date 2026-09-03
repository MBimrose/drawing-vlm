from build123d import *

vertical_leg_length = 60.0
horizontal_leg_length = 80.0
thickness = 10.0
inner_fillet_radius = 2.0
blind_hole_diameter = 6.0
blind_hole_depth = 30.0
through_hole_diameter = 5.0
through_hole_spacing = 20.0
through_hole_offset = 15.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0,0), (0, vertical_leg_length), (thickness, vertical_leg_length),
                     (thickness, thickness), (horizontal_leg_length, thickness),
                     (horizontal_leg_length, 0), close=True)
        make_face()
    extrude(amount=thickness)

solid = p.part
inner_edge = solid.edges().filter_by(Axis.Z).sort_by(Axis.X)[2]
solid = fillet([inner_edge], inner_fillet_radius)

solid = solid - Pos(thickness/2, vertical_leg_length - blind_hole_depth/2, thickness/2) * Rot(90, 0, 0) * Cylinder(blind_hole_diameter/2, blind_hole_depth)

for i in range(3):
    x = thickness + through_hole_offset + i * through_hole_spacing
    solid = solid - Pos(x, thickness/2, thickness) * Cylinder(through_hole_diameter/2, thickness)

part = solid
part.name = "L_Bracket"
export_step(part, "output.step")