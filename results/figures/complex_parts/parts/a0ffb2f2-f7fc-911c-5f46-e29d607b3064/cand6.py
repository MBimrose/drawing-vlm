from build123d import *

shaft_radius = 5.0
shaft_length = 60.0
head_radius = 15.0
head_thickness = 10.0
thread_diameter = 8.0
thread_depth = 5.0
slot_width = 2.0
slot_depth = 1.5
slot_length = 30.0
chamfer_size = 0.5

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            l1 = Line((0, 0), (shaft_radius, 0))
            l2 = Line(l1 @ 1, (shaft_radius, shaft_length - head_thickness))
            l3 = Line(l2 @ 1, (head_radius, shaft_length - head_thickness))
            l4 = Line(l3 @ 1, (head_radius, shaft_length))
            l5 = Line(l4 @ 1, (0, shaft_length))
            l6 = Line(l5 @ 1, (0, 0))
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part

# Thread hole from top face
solid_body = solid_body - Pos(0, 0, shaft_length - thread_depth / 2) * Cylinder(thread_diameter / 2, thread_depth)

# Slot cut
slot_box = Pos(0, 0, shaft_length / 2) * Box(slot_width, slot_depth, slot_length)
solid_body = solid_body - slot_box

# Chamfer top edges
top_face = solid_body.faces().sort_by(Axis.Z)[-1]
top_edges = top_face.edges()
solid_body = chamfer(top_edges, chamfer_size)

part = solid_body
part.name = "shaft_with_head"
export_step(part, "output.step")