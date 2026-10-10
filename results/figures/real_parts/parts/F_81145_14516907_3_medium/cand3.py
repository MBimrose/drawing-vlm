from build123d import *

outer_diameter = 80.0
wall_thickness = 5.0
length = 70.0
thread_diameter = 15.0
thread_length = 30.0
slot_width = 10.0
slot_depth = 4.0
chamfer_size = 2.0

outer_radius = outer_diameter / 2.0
inner_radius = outer_radius - wall_thickness
thread_radius = thread_diameter / 2.0

with BuildPart() as p:
    with BuildSketch(Plane.XY) as sk:
        with BuildLine() as bl:
            l1 = Line((0, 0), (outer_radius, 0))
            l2 = Line(l1 @ 1, (outer_radius, wall_thickness))
            l3 = Line(l2 @ 1, (inner_radius, wall_thickness))
            l4 = Line(l3 @ 1, (inner_radius, length - thread_length))
            l5 = Line(l4 @ 1, (thread_radius, length - thread_length))
            l6 = Line(l5 @ 1, (thread_radius, length))
            l7 = Line(l6 @ 1, (0, length))
            l8 = Line(l7 @ 1, (0, 0))
        make_face()
    revolve(axis=Axis.Y)

solid_body = p.part

thread_cyl = Pos(0, length - thread_length / 2, 0) * Rot(90, 0, 0) * Cylinder(thread_radius, thread_length)
solid_body = solid_body - thread_cyl

slot_box = Pos(0, length / 2, 0) * Box(slot_width, slot_depth, length)
solid_body = solid_body - slot_box

top_face = solid_body.faces().sort_by(Axis.Y)[-1]
top_edges = top_face.edges()
solid_body = chamfer(top_edges, chamfer_size)

part = solid_body
part.name = "revolved_tube_with_thread_and_slot"
export_step(part, "output.step")