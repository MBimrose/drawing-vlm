from build123d import *

bracket_length = 80.0
bracket_width = 50.0
bracket_thickness = 12.0
gusset_height = 30.0
gusset_thickness = 10.0
hole_diameter = 6.0
hole_spacing = 25.0
hole_offset_from_edge = 15.0
chamfer_distance = 5.0
rib_height = 10.0
rib_thickness = 5.0
rib_spacing = 20.0

with BuildPart() as p:
    with BuildSketch() as s:
        with BuildLine() as l:
            Polyline((0, 0), (bracket_length, 0), (bracket_length, bracket_width - gusset_height),
                     (bracket_length - gusset_thickness, bracket_width), (0, bracket_width), close=True)
        make_face()
    extrude(amount=bracket_thickness)

solid_body = p.part
solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_distance)

for i in range(3):
    x = hole_offset_from_edge + i * hole_spacing
    y = bracket_width / 2
    solid_body = solid_body - Pos(x, y, 0) * Cylinder(hole_diameter / 2, bracket_thickness * 2)

rib1 = Pos(bracket_length / 2 - rib_spacing / 2, bracket_width / 2, -rib_height / 2) * Box(rib_thickness, rib_height, rib_height)
rib2 = Pos(bracket_length / 2 + rib_spacing / 2, bracket_width / 2, -rib_height / 2) * Box(rib_thickness, rib_height, rib_height)
solid_body = solid_body + rib1 + rib2

part = solid_body
part.name = "bracket_with_gusset_and_ribs"
export_step(part, "output.step")