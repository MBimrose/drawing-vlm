from build123d import *

long_leg = 80.0
short_leg = 50.0
thickness = 8.0
inner_fillet = 2.0
hole_diameter = 5.0
hole_spacing = 12.0
hole_offset = 15.0
mount_hole_diameter = 6.0
mount_hole_spacing = 20.0
mount_hole_offset = 10.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0, 0), (long_leg, 0), (long_leg, thickness), (thickness, thickness), (thickness, short_leg), (0, short_leg), close=True)
        make_face()
    extrude(amount=thickness)

solid_body = p.part
solid_body = fillet(solid_body.edges().filter_by(Axis.Z), inner_fillet)

for i in range(4):
    x = hole_offset + i * hole_spacing
    y = thickness / 2
    solid_body = solid_body - Pos(x, y, 0) * Cylinder(hole_diameter / 2, thickness * 2)

for i in range(2):
    y = mount_hole_offset + i * mount_hole_spacing
    z = thickness / 2
    solid_body = solid_body - Pos(0, y, z) * Rot(0, 90, 0) * Cylinder(mount_hole_diameter / 2, long_leg * 2)

part = solid_body
part.name = "L_Bracket"
export_step(part, "output.step")