from build123d import *

head_diameter = 30.0
head_height = 10.0
shank_diameter = 10.0
shank_length = 50.0
wall_thickness = 2.0
slot_width = 5.0
slot_length = 20.0
slot_depth = 3.0
chamfer_size = 1.0

head_radius = head_diameter / 2.0
shank_radius = shank_diameter / 2.0
total_length = shank_length + head_height

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            l1 = Line((0, 0), (shank_radius, 0))
            l2 = Line(l1 @ 1, (shank_radius, shank_length))
            l3 = Line(l2 @ 1, (head_radius, shank_length))
            l4 = Line(l3 @ 1, (head_radius, total_length))
            l5 = Line(l4 @ 1, (0, total_length))
            l6 = Line(l5 @ 1, (0, 0))
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part
top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[top_face])

slot_box = Pos(0, 0, total_length - slot_depth / 2) * Box(slot_width, slot_length, slot_depth)
solid_body = solid_body - slot_box

top_edges = solid_body.edges().sort_by(Axis.Z)[-1:]
solid_body = chamfer(top_edges, chamfer_size)

part = solid_body
part.name = "revolved_hollow_pin_with_slot"
export_step(part, "output.step")