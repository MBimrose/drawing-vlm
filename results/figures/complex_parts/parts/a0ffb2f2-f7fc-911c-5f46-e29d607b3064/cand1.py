from build123d import *

head_diameter = 30.0
head_height = 10.0
shank_diameter = 10.0
shank_length = 45.0
thread_diameter = 8.0
thread_depth = 6.0
slot_width = 4.0
slot_length = 12.0
slot_depth = 3.0
pocket_width = 6.0
pocket_height = 4.0
pocket_depth = 2.0

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            l1 = Line((0, 0), (shank_diameter / 2, 0))
            l2 = Line(l1 @ 1, (shank_diameter / 2, shank_length))
            l3 = Line(l2 @ 1, (head_diameter / 2, shank_length))
            l4 = Line(l3 @ 1, (head_diameter / 2, shank_length + head_height))
            l5 = Line(l4 @ 1, (0, shank_length + head_height))
            l6 = Line(l5 @ 1, (0, 0))
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part
top_z = shank_length + head_height

solid_body = solid_body - Pos(0, 0, top_z - thread_depth / 2) * Cylinder(thread_diameter / 2, thread_depth)
solid_body = solid_body - Pos(0, 0, top_z - slot_depth / 2) * Box(slot_width, slot_length, slot_depth)
solid_body = solid_body - Pos(head_diameter / 4, 0, top_z - pocket_depth / 2) * Box(pocket_width, pocket_height, pocket_depth)

part = solid_body
part.name = "revolved_shaft_with_head"
export_step(part, "output.step")