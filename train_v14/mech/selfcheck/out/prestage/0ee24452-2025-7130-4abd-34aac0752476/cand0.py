from build123d import *

vertical_leg_length = 70.0
horizontal_leg_length = 60.0
thickness = 8.0
extrude_depth = 20.0
notch_width = 10.0
notch_depth = 5.0
hole_diameter = 5.0
hole_spacing = 20.0
hole_offset = 10.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0, 0), (0, vertical_leg_length), (thickness, vertical_leg_length),
                     (thickness, vertical_leg_length - notch_depth), (thickness + notch_width, vertical_leg_length),
                     (thickness, vertical_leg_length), (thickness, thickness),
                     (horizontal_leg_length, thickness), (horizontal_leg_length, 0), close=True)
        make_face()
    extrude(amount=extrude_depth)

solid_body = p.part

for i in range(2):
    x = hole_offset + i * hole_spacing
    solid_body = solid_body - Pos(x, vertical_leg_length, extrude_depth / 2) * Rot(90, 0, 0) * Cylinder(hole_diameter / 2, 200)

for i in range(2):
    y = hole_offset + i * hole_spacing
    solid_body = solid_body - Pos(horizontal_leg_length, y, extrude_depth / 2) * Rot(0, 90, 0) * Cylinder(hole_diameter / 2, 200)

part = solid_body
part.name = "L_Bracket"
export_step(part, "output.step")