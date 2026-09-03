from build123d import *

bracket_length = 80.0
bracket_width = 30.0
bracket_thickness = 8.0
leg_extension = 20.0
rib_width = 5.0
rib_height = 6.0
rib_depth = 2.0
rib_spacing = 15.0
rib_offset = 10.0
hole_diameter = 5.0
chamfer_size = 1.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0, 0), (bracket_length, 0), (bracket_length, bracket_width),
                     (bracket_width, bracket_width), (bracket_width, bracket_width + leg_extension),
                     (0, bracket_width + leg_extension), close=True)
        make_face()
    extrude(amount=bracket_thickness)

solid_body = p.part
solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_size)

rib_count = int((bracket_length - 2 * rib_offset) // rib_spacing) + 1
for i in range(rib_count):
    x_pos = rib_offset + i * rib_spacing
    rib = Pos(x_pos, bracket_width, bracket_thickness - rib_height / 2) * Box(rib_width, rib_depth, rib_height)
    solid_body = solid_body + rib

hole = Pos(bracket_width / 2, bracket_width / 2, bracket_thickness / 2) * Cylinder(hole_diameter / 2, bracket_thickness)
solid_body = solid_body - hole

part = solid_body
part.name = "L_bracket_with_ribs"
export_step(part, "output.step")