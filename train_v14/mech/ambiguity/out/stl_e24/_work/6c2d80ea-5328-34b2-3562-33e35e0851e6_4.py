from build123d import *

vertical_height = 80.0
horizontal_length = 70.0
thickness = 10.0
depth = 8.0
gusset_width = 12.0
gusset_height = 12.0
hole_diameter = 4.0
hole_depth = 4.0
hole_spacing = 15.0
hole_offset = 20.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0, 0), (0, vertical_height), (thickness, vertical_height),
                     (thickness, thickness), (horizontal_length, thickness),
                     (horizontal_length, 0), close=True)
        make_face()
    extrude(amount=depth)

with BuildPart() as g:
    with BuildSketch() as gsk:
        with BuildLine() as gbl:
            Polyline((0, 0), (gusset_width, 0), (0, gusset_height), close=True)
        make_face()
    extrude(amount=depth)

solid_body = p.part + g.part

for i in range(3):
    x = hole_offset + i * hole_spacing
    y = thickness / 2
    solid_body = solid_body - Pos(x, y, depth - hole_depth / 2) * Cylinder(hole_diameter / 2, hole_depth)

part = solid_body
part.name = "L_Bracket"
export_step(part, "output.step")