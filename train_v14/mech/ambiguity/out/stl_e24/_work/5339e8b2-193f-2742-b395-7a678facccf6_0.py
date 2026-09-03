from build123d import *

long_leg_length = 80.0
short_leg_length = 40.0
leg_width = 20.0
thickness = 8.0
hole_diameter = 5.0
hole_offset_from_end = 12.0
rib_width = 5.0
rib_height = 6.0
rib_depth = 2.0
rib_spacing = 15.0
chamfer_size = 1.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0, 0), (long_leg_length, 0), (long_leg_length, leg_width),
                     (leg_width, leg_width), (leg_width, short_leg_length + leg_width),
                     (0, short_leg_length + leg_width), close=True)
        make_face()
    extrude(amount=thickness)

solid_body = p.part
solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_size)

hole_x = long_leg_length - hole_offset_from_end
hole_y = leg_width / 2
solid_body = solid_body - Pos(hole_x, hole_y, thickness / 2) * Cylinder(hole_diameter / 2, thickness)

rib_count = int((long_leg_length - 2 * rib_spacing) // rib_spacing)
for i in range(rib_count):
    rib_x = rib_spacing + i * rib_spacing
    rib_y = leg_width / 2
    solid_body = solid_body - Pos(rib_x, rib_y, thickness - rib_depth / 2) * Box(rib_width, rib_height, rib_depth)

part = solid_body
part.name = "L_Bracket"
export_step(part, "output.step")