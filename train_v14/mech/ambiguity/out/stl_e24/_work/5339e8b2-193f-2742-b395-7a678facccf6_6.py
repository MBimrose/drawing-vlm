from build123d import *

bracket_length = 80
bracket_width = 40
bracket_thickness = 8
gusset_height = 20
gusset_width = 30
hole_diameter = 5
chamfer_distance = 1
rib_width = 5
rib_height = 6
rib_depth = 1
rib_spacing = 15
rib_count = 3

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0, 0), (bracket_length, 0), (bracket_length, bracket_width),
                     (gusset_width, bracket_width), (gusset_width, bracket_width + gusset_height),
                     (0, bracket_width + gusset_height), close=True)
        make_face()
    extrude(amount=bracket_thickness)

solid_body = p.part
solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_distance)

hole_center_x = bracket_length / 2
hole_center_y = (bracket_width + gusset_height) / 2
solid_body = solid_body - Pos(hole_center_x, hole_center_y, 0) * Cylinder(hole_diameter / 2, bracket_thickness * 2)

for i in range(rib_count):
    rib_x = 10 + i * rib_spacing
    rib_y = bracket_width / 2
    solid_body = solid_body - Pos(rib_x, rib_y, bracket_thickness - rib_depth / 2) * Box(rib_width, rib_height, rib_depth)

part = solid_body
part.name = "bracket_with_gusset"
export_step(part, "output.step")