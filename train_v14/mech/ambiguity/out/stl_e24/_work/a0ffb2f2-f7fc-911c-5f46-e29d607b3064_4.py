from build123d import *

shaft_diameter = 10.0
shaft_radius = shaft_diameter / 2.0
shaft_length = 55.0
shoulder_diameter = 30.0
shoulder_radius = shoulder_diameter / 2.0
shoulder_length = 10.0
total_length = shaft_length + shoulder_length
bore_diameter = 8.0
bore_radius = bore_diameter / 2.0
counterbore_diameter = 12.0
counterbore_radius = counterbore_diameter / 2.0
counterbore_depth = 5.0
keyway_width = 4.0
keyway_depth = 3.0
keyway_length = 45.0
keyway_offset = 15.0
slot_width = 6.0
slot_depth = 4.0
slot_length = 20.0
slot_offset = 15.0
chamfer_size = 1.0

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            l1 = Line((0, 0), (shaft_radius, 0))
            l2 = Line(l1@1, (shaft_radius, shaft_length))
            l3 = Line(l2@1, (shoulder_radius, shaft_length))
            l4 = Line(l3@1, (shoulder_radius, total_length))
            l5 = Line(l4@1, (0, total_length))
            l6 = Line(l5@1, (0, 0))
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part
solid_body = solid_body - Pos(0, 0, total_length / 2) * Cylinder(bore_radius, total_length)
solid_body = solid_body - Pos(0, 0, total_length - counterbore_depth / 2) * Cylinder(counterbore_radius, counterbore_depth)
solid_body = solid_body - Pos(0, 0, keyway_offset + keyway_length / 2) * Box(keyway_width, keyway_depth, keyway_length)
solid_body = solid_body - Pos(0, 0, slot_offset + slot_length / 2) * Box(slot_width, slot_depth, slot_length)
top_edges = solid_body.edges().sort_by(Axis.Z)[-1:]
solid_body = chamfer(top_edges, chamfer_size)

part = solid_body
part.name = "stepped_shaft_with_keyway"
export_step(part, "output.step")