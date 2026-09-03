from build123d import *

knob_diameter = 50.0
knob_length = 30.0
rib_height = 5.0
rib_thickness = 2.0
rib_count = 12
bore_diameter = 12.0
chamfer_distance = 1.0
hex_flat_distance = 10.0
hex_depth = 5.0

result = Cylinder(knob_diameter / 2, knob_length)
result = result - Cylinder(bore_diameter / 2, knob_length)

top_face = result.faces().sort_by(Axis.Z)[-1]
result = chamfer(top_face.edges(), chamfer_distance)

with BuildPart() as hp:
    with BuildSketch() as hs:
        RegularPolygon(hex_flat_distance, 6)
    extrude(amount=hex_depth)
result = result - Pos(0, 0, knob_length - hex_depth) * hp.part

rib = Box(rib_height, rib_thickness, knob_length)
rib_x = knob_diameter / 2 + rib_thickness / 2
rib_z = knob_length / 2

for i in range(rib_count):
    angle = i * 360.0 / rib_count
    result = result + Rot(0, 0, angle) * Pos(rib_x, 0, rib_z) * rib

part = result
part.name = "knob_with_ribs"
export_step(part, "output.step")