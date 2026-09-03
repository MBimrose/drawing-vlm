from build123d import *

knob_outer_diameter = 50.0
knob_height = 30.0
shaft_diameter = 12.0
knurl_height = 5.0
knurl_width = 2.0
knurl_depth = 2.0
knurl_count = 12
pocket_diameter = 20.0
pocket_depth = 8.0
chamfer_size = 1.0

solid_body = Cylinder(knob_outer_diameter / 2, knob_height)
solid_body = solid_body - Cylinder(shaft_diameter / 2, knob_height)

pocket = Pos(0, 0, knob_height - pocket_depth / 2) * Cylinder(pocket_diameter / 2, pocket_depth)
solid_body = solid_body - pocket

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = chamfer(top_face.edges(), chamfer_size)

knurl_radius = knob_outer_diameter / 2 + knurl_depth / 2
for i in range(knurl_count):
    angle = i * 360.0 / knurl_count
    rib = Rot(0, 0, angle) * Pos(knurl_radius, 0, knob_height / 2) * Box(knurl_height, knurl_depth, knob_height - pocket_depth)
    solid_body = solid_body + rib

part = solid_body
part.name = "knob"
export_step(part, "output.step")