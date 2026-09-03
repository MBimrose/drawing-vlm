from build123d import *

bracket_length = 80.0
bracket_width = 50.0
bracket_thickness = 8.0
gusset_height = 30.0
gusset_thickness = 6.0
hole_diameter = 5.0
hole_spacing_x = 20.0
hole_spacing_y = 20.0
hole_rows = 2
hole_cols = 3
chamfer_size = 0.5
rib_thickness = 3.0
rib_height = 5.0
rib_spacing = 15.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0, 0), (bracket_length, 0), (bracket_length, bracket_thickness),
                     (bracket_length + gusset_height, bracket_thickness),
                     (bracket_length, bracket_thickness + gusset_thickness),
                     (bracket_length, bracket_width), (0, bracket_width), close=True)
        make_face()
    extrude(amount=bracket_thickness)

solid_body = p.part
solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_size)

x_start = (bracket_length - (hole_cols - 1) * hole_spacing_x) / 2
y_start = (bracket_width - (hole_rows - 1) * hole_spacing_y) / 2
for i in range(hole_cols):
    for j in range(hole_rows):
        x = x_start + i * hole_spacing_x
        y = y_start + j * hole_spacing_y
        solid_body = solid_body - Pos(x, y, bracket_thickness / 2) * Cylinder(hole_diameter / 2, bracket_thickness)

rib_count = int((bracket_width - 2 * rib_spacing) / rib_spacing) + 1
for i in range(rib_count):
    y = rib_spacing + i * rib_spacing
    solid_body = solid_body - Pos(bracket_length / 2, y, rib_height / 2) * Box(rib_thickness, bracket_thickness, rib_height)

part = solid_body
part.name = "bracket_with_gusset"
export_step(part, "output.step")