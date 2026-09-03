from build123d import *

horizontal_length = 80.0
vertical_length = 70.0
thickness = 10.0
bracket_depth = 12.0
fillet_radius = 2.0
pocket_width = 8.0
pocket_height = 30.0
pocket_depth = 4.0
pocket_offset_from_top = 15.0
tap_hole_diameter = 4.5
tap_hole_depth = 8.0
tap_hole_offset_from_top = 5.0
mount_hole_diameter = 6.0
mount_hole_spacing = 30.0
mount_hole_offset = 20.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0, 0), (horizontal_length, 0), (horizontal_length, thickness),
                     (thickness, thickness), (thickness, vertical_length), (0, vertical_length), close=True)
        make_face()
    extrude(amount=bracket_depth)

solid_body = p.part
solid_body = fillet(solid_body.edges().filter_by(Axis.Z), fillet_radius)

pocket_cx = thickness / 2
pocket_cy = vertical_length - pocket_offset_from_top - pocket_height / 2
pocket_box = Pos(pocket_cx, pocket_cy, bracket_depth - pocket_depth / 2) * Box(pocket_width, pocket_height, pocket_depth)
solid_body = solid_body - pocket_box

tap_cx = thickness / 2
tap_cy = vertical_length - tap_hole_offset_from_top
tap_cyl = Pos(tap_cx, tap_cy, bracket_depth - tap_hole_depth / 2) * Cylinder(tap_hole_diameter / 2, tap_hole_depth)
solid_body = solid_body - tap_cyl

for x, y in [(horizontal_length / 2, thickness / 2), (thickness / 2, vertical_length / 2)]:
    mount_cyl = Pos(x, y, 0) * Cylinder(mount_hole_diameter / 2, bracket_depth + 1)
    solid_body = solid_body - mount_cyl

part = solid_body
part.name = "L_Bracket"
export_step(part, "output.step")