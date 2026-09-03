from build123d import *

leg_length = 80.0
leg_width = 30.0
thickness = 5.0
bracket_depth = 10.0
fillet_radius = 2.0
chamfer_distance = 1.0
hole_diameter = 4.0
hole_spacing = 15.0
hole_offset = 10.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0, 0), (leg_length, 0), (leg_length, thickness),
                     (thickness, thickness), (thickness, leg_width),
                     (0, leg_width), close=True)
        make_face()
    extrude(amount=bracket_depth)

solid_body = p.part
solid_body = fillet(solid_body.edges(), fillet_radius)
solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_distance)

hole_r = hole_diameter / 2
hole_h = bracket_depth + 1.0
for i in range(3):
    x = hole_offset + i * hole_spacing
    y = thickness / 2
    solid_body = solid_body - Pos(x, y, bracket_depth / 2) * Cylinder(hole_r, hole_h)

for i in range(3):
    x = thickness / 2
    y = hole_offset + i * hole_spacing
    solid_body = solid_body - Pos(x, y, bracket_depth / 2) * Cylinder(hole_r, hole_h)

part = solid_body
part.name = "L_bracket"
export_step(part, "output.step")