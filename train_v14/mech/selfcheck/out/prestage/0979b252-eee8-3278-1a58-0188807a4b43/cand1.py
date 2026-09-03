from build123d import *

jaw_length = 80.0
jaw_width = 30.0
jaw_thickness = 8.0
rib_height = 2.0
rib_width = 4.0
rib_spacing = 10.0
hole_diameter = 5.0
hole_offset = 20.0
chamfer_dist = 0.5
hex_radius = 6.0
hex_depth = 2.0

with BuildPart() as p:
    with BuildSketch() as s:
        Rectangle(jaw_length, jaw_width)
    extrude(amount=jaw_thickness)

solid_body = p.part

for x, y in [(-jaw_length/2 + hole_offset, 0), (jaw_length/2 - hole_offset, 0)]:
    solid_body = solid_body - Pos(x, y, jaw_thickness/2) * Cylinder(hole_diameter/2, jaw_thickness + 2)

solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_dist)

rib_count = int((jaw_width - 2 * rib_spacing) // (rib_width + rib_spacing))
for i in range(rib_count):
    y_pos = -jaw_width/2 + rib_spacing + i * (rib_width + rib_spacing) + rib_width/2
    solid_body = solid_body + Pos(0, y_pos, jaw_thickness/2) * Box(jaw_length, rib_width, rib_height)

with BuildPart() as hp:
    with BuildSketch() as hs:
        RegularPolygon(hex_radius, 6)
    extrude(amount=hex_depth)
hex_solid = hp.part
solid_body = solid_body - Pos(0, 0, jaw_thickness - hex_depth/2) * hex_solid

part = solid_body
part.name = "jaw_plate"
export_step(part, "output.step")