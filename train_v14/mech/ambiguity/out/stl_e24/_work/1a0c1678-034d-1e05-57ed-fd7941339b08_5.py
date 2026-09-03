from build123d import *

leg_length = 70.0
leg_height = 50.0
thickness = 8.0
fillet_radius = 2.0
hole_diameter = 5.0
hole_spacing = 12.0
hole_offset = 15.0
mount_hole_diameter = 6.0
mount_hole_spacing = 20.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0, 0), (leg_length, 0), (leg_length, thickness), (thickness, thickness), (thickness, leg_height), (0, leg_height), close=True)
        make_face()
    extrude(amount=thickness)

solid_body = p.part
solid_body = fillet(solid_body.edges().filter_by(Axis.Z), fillet_radius)

for i in range(4):
    x = hole_offset + i * hole_spacing
    y = thickness / 2
    solid_body = solid_body - Pos(x, y, 0) * Cylinder(hole_diameter / 2, thickness * 2)

for i in range(2):
    y = leg_height / 2 - mount_hole_spacing / 2 + i * mount_hole_spacing
    solid_body = solid_body - Pos(0, y, 0) * Rot(0, 90, 0) * Cylinder(mount_hole_diameter / 2, leg_length * 2)

part = solid_body
part.name = "L_Bracket"
export_step(part, "output.step")