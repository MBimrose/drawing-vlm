from build123d import *

outer_radius = 30.0
inner_radius = 10.0
height = 45.0
shoulder_height = 10.0
shoulder_radius = 22.0
chamfer_distance = 2.0
hole_diameter = 10.0
slot_width = 8.0
slot_depth = 20.0

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            l1 = Line((0, 0), (outer_radius, 0))
            l2 = Line(l1 @ 1, (outer_radius, height - shoulder_height))
            l3 = Line(l2 @ 1, (shoulder_radius, height - shoulder_height))
            l4 = Line(l3 @ 1, (shoulder_radius, height))
            l5 = Line(l4 @ 1, (0, height))
            l6 = Line(l5 @ 1, (0, 0))
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
top_edges = top_face.edges()
solid_body = chamfer(top_edges, chamfer_distance)

solid_body = solid_body - Cylinder(hole_diameter / 2, height)

slot_box = Pos(outer_radius - slot_depth / 2, 0, height / 2) * Box(slot_depth, 2 * outer_radius, height)
solid_body = solid_body - slot_box

part = solid_body
part.name = "revolved_part_with_hole_and_slot"
export_step(part, "output.step")