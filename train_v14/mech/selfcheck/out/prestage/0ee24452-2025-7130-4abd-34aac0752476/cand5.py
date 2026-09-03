from build123d import *

leg_length = 70.0
leg_width = 60.0
thickness = 8.0
extrude_depth = 20.0
hole_diameter = 5.0
hole_spacing = 20.0
hole_offset = 10.0
chamfer_size = 1.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0, 0), (leg_width, 0), (leg_width, thickness), (thickness, thickness), (thickness, leg_length), (0, leg_length), close=True)
        make_face()
    extrude(amount=extrude_depth)

solid_body = p.part

for i in range(3):
    x = hole_offset + i * hole_spacing
    solid_body = solid_body - Pos(x, leg_length, extrude_depth / 2) * Rot(90, 0, 0) * Cylinder(hole_diameter / 2, 200)

part = solid_body
part.name = "L_bracket"
export_step(part, "output.step")