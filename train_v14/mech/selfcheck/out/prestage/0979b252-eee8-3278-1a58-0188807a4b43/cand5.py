from build123d import *

jaw_length = 80.0
jaw_width = 30.0
jaw_thickness = 8.0
rib_height = 4.0
rib_width = 6.0
rib_length = jaw_length - 20.0
hole_diameter = 5.0
hole_spacing = 40.0
chamfer_size = 0.5
hex_radius = 5.0
hex_depth = 2.0
side_rib_width = 4.0
side_rib_height = 3.0
side_rib_offset = 10.0

base = Box(jaw_length, jaw_width, jaw_thickness)
central_rib = Box(rib_length, rib_width, rib_height)
side_rib1 = Pos(-jaw_length/2 + side_rib_offset, 0, 0) * Box(side_rib_width, side_rib_height, rib_height)
side_rib2 = Pos(jaw_length/2 - side_rib_offset, 0, 0) * Box(side_rib_width, side_rib_height, rib_height)

solid_body = base + central_rib + side_rib1 + side_rib2

solid_body = solid_body - Pos(-hole_spacing/2, 0, 0) * Cylinder(hole_diameter/2, jaw_thickness + 10)
solid_body = solid_body - Pos(hole_spacing/2, 0, 0) * Cylinder(hole_diameter/2, jaw_thickness + 10)

with BuildPart() as hp:
    with BuildSketch() as hs:
        RegularPolygon(hex_radius, 6)
    extrude(amount=hex_depth)
hex_prism = Pos(0, 0, jaw_thickness/2 - hex_depth/2) * hp.part
solid_body = solid_body - hex_prism

vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = chamfer(vertical_edges, chamfer_size)

part = solid_body
part.name = "jaw_with_ribs"
export_step(part, "output.step")