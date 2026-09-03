from build123d import *

leg_length = 80.0
leg_width = 20.0
leg_thickness = 8.0
flange_length = 40.0
flange_width = 20.0
hole_diameter = 5.0
hole_offset = 10.0
chamfer_size = 1.0
rib_width = 5.0
rib_height = 6.0
rib_depth = 1.0
rib_spacing = 15.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0, 0), (leg_length, 0), (leg_length, leg_width),
                     (flange_length, leg_width), (flange_length, leg_width + flange_width),
                     (0, leg_width + flange_width), close=True)
        make_face()
    extrude(amount=leg_thickness)

solid_body = p.part
solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_size)

hole_x = leg_length - hole_offset
hole_y = leg_width / 2.0
solid_body = solid_body - Pos(hole_x, hole_y, leg_thickness / 2) * Cylinder(hole_diameter / 2, leg_thickness + 2)

rib_count = int((leg_length - flange_length) // rib_spacing)
for i in range(rib_count):
    rib_x = flange_length + rib_spacing / 2.0 + i * rib_spacing
    rib_y = leg_width
    solid_body = solid_body - Pos(rib_x, rib_y, leg_thickness - rib_depth / 2) * Box(rib_width, rib_height, rib_depth)

part = solid_body
part.name = "L_bracket_with_ribs"
export_step(part, "output.step")