from build123d import *

horizontal_length = 80.0
vertical_height = 50.0
thickness = 8.0
fillet_radius = 2.0
hole_diameter = 5.0
hole_spacing = 12.0
hole_offset_from_end = 15.0
mount_hole_diameter = 6.0
mount_hole_spacing = 20.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0, 0), (horizontal_length, 0), (horizontal_length, thickness),
                     (thickness, thickness), (thickness, vertical_height), (0, vertical_height), close=True)
        make_face()
    extrude(amount=thickness)

solid_body = p.part
solid_body = fillet(solid_body.edges().filter_by(Axis.Z), fillet_radius)

for i in range(4):
    x = hole_offset_from_end + i * hole_spacing
    y = thickness / 2
    solid_body = solid_body - Pos(x, y, 0) * Cylinder(hole_diameter / 2, thickness * 2)

for i in range(2):
    y = vertical_height / 2 + (i - 0.5) * mount_hole_spacing
    solid_body = solid_body - Pos(0, y, 0) * Rot(0, 90, 0) * Cylinder(mount_hole_diameter / 2, horizontal_length)

part = solid_body
part.name = "L_Bracket"
export_step(part, "output.step")