from build123d import *

long_leg_length = 80.0
short_leg_length = 50.0
thickness = 8.0
inner_fillet_radius = 2.0
mount_hole_diameter = 6.0
mount_hole_spacing = 20.0
mount_hole_offset = 10.0
clearance_hole_diameter = 5.0
clearance_hole_spacing = 12.0
clearance_hole_start = 15.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0, 0), (long_leg_length, 0), (long_leg_length, thickness),
                     (thickness, thickness), (thickness, short_leg_length),
                     (0, short_leg_length), close=True)
        make_face()
    extrude(amount=thickness)

solid_body = p.part
solid_body = fillet(solid_body.edges().filter_by(Axis.Z), inner_fillet_radius)

for i in range(2):
    y_pos = mount_hole_offset + i * mount_hole_spacing
    solid_body = solid_body - Pos(0, y_pos, 0) * Rot(0, 90, 0) * Cylinder(mount_hole_diameter / 2, 100)

for i in range(4):
    x_pos = clearance_hole_start + i * clearance_hole_spacing
    solid_body = solid_body - Pos(x_pos, thickness / 2, 0) * Cylinder(clearance_hole_diameter / 2, 100)

part = solid_body
part.name = "L_Bracket"
export_step(part, "output.step")