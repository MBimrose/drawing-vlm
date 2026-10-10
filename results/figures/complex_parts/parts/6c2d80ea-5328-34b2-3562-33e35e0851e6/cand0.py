from build123d import *

leg_length = 80.0
leg_width = 60.0
thickness = 8.0
rib_height = 12.0
rib_base = 12.0
hole_diameter = 4.0
hole_depth = thickness - 2.0
hole_spacing = 15.0
hole_offset = 20.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0, 0), (0, leg_length), (thickness, leg_length),
                     (thickness, thickness), (leg_width, thickness),
                     (leg_width, 0), close=True)
        make_face()
    extrude(amount=thickness)

solid_body = p.part

with BuildPart() as rib_p:
    with BuildSketch() as rib_sk:
        with BuildLine() as rib_bl:
            Polyline((0, 0), (rib_base, 0), (0, rib_height), close=True)
        make_face()
    extrude(amount=thickness)

solid_body = solid_body + rib_p.part

for i in range(3):
    x = hole_offset + i * hole_spacing
    y = thickness / 2
    solid_body = solid_body - Pos(x, y, thickness) * Cylinder(hole_diameter / 2, hole_depth)

part = solid_body
part.name = "L_Bracket"
export_step(part, "output.step")