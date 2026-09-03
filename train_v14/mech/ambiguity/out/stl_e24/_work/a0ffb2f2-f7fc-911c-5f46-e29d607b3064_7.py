from build123d import *

shaft_diameter = 10.0
shaft_length = 55.0
head_diameter = 30.0
head_thickness = 10.0
keyway_width = 4.0
keyway_depth = 2.0
head_hole_diameter = 8.0
head_hole_offset = 15.0
counterbore_diameter = 10.0
counterbore_depth = 5.0
chamfer_size = 1.0

shaft_radius = shaft_diameter / 2.0
head_radius = head_diameter / 2.0

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            l1 = Line((0, 0), (shaft_radius, 0))
            l2 = Line(l1 @ 1, (shaft_radius, shaft_length))
            l3 = Line(l2 @ 1, (head_radius, shaft_length))
            l4 = Line(l3 @ 1, (head_radius, shaft_length + head_thickness))
            l5 = Line(l4 @ 1, (0, shaft_length + head_thickness))
            l6 = Line(l5 @ 1, (0, 0))
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part

keyway_box = Pos(shaft_radius - keyway_depth / 2.0, 0, shaft_length / 2.0) * Box(keyway_depth, keyway_width, shaft_length)
solid_body = solid_body - keyway_box

head_center_z = shaft_length + head_thickness / 2.0
hole_center_x = head_radius - head_hole_offset

through_hole = Pos(hole_center_x, 0, head_center_z) * Cylinder(head_hole_diameter / 2.0, head_thickness + 10)
solid_body = solid_body - through_hole

cbore = Pos(hole_center_x, 0, head_center_z + head_thickness / 2.0 - counterbore_depth / 2.0) * Cylinder(counterbore_diameter / 2.0, counterbore_depth)
solid_body = solid_body - cbore

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
top_edges = top_face.edges()
solid_body = chamfer(top_edges, chamfer_size)

part = solid_body
part.name = "pin_with_keyway"
export_step(part, "output.step")