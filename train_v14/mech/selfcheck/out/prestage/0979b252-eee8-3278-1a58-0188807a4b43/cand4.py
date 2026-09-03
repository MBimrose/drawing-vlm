from build123d import *

jaw_length = 80.0
jaw_width = 30.0
jaw_thickness = 8.0
hex_flat_distance = 10.0
hex_depth = 4.0
hole_diameter = 5.0
hole_spacing = 40.0
chamfer_distance = 0.5

with BuildPart() as p:
    with BuildSketch() as s:
        Rectangle(jaw_length, jaw_width)
    extrude(amount=jaw_thickness)

solid_body = p.part

with BuildPart() as hp:
    with BuildSketch() as hs:
        RegularPolygon(hex_flat_distance/2, 6)
    extrude(amount=hex_depth)

hex_prism = hp.part
solid_body = solid_body - Pos(0, 0, jaw_thickness - hex_depth/2) * hex_prism

for x in [-hole_spacing/2, hole_spacing/2]:
    solid_body = solid_body - Pos(x, 0, jaw_thickness/2) * Cylinder(hole_diameter/2, jaw_thickness)

vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = chamfer(vertical_edges, chamfer_distance)

part = solid_body
part.name = "jaw_with_hex_cutout"
export_step(part, "output.step")