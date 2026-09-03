from build123d import *

leg_length_long = 80.0
leg_length_short = 60.0
leg_width = 20.0
thickness = 10.0
relief_width = 4.0
relief_height = 20.0
hole_diameter = 5.0
hole_depth = 8.0
hole_spacing = 12.0
hole_count = 4
chamfer_size = 0.5

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0, 0), (0, leg_length_long), (thickness, leg_length_long),
                     (thickness, leg_width), (leg_length_short + thickness, leg_width),
                     (leg_length_short + thickness, 0), close=True)
        make_face()
    extrude(amount=thickness)

solid_body = p.part

relief = Pos(thickness/2, leg_length_long/2, thickness/2) * Box(relief_width, relief_height, thickness)
solid_body = solid_body - relief

for i in range(hole_count):
    x = leg_width + i * hole_spacing
    y = leg_width / 2
    hole = Pos(x, y, thickness - hole_depth/2) * Cylinder(hole_diameter/2, hole_depth)
    solid_body = solid_body - hole

solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_size)

part = solid_body
part.name = "L_Bracket"
export_step(part, "output.step")