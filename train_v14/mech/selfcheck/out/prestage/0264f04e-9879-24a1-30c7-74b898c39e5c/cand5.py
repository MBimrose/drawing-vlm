from build123d import *

base_radius = 30.0
base_height = 15.0
step_radius = 20.0
step_height = 15.0
top_radius = 12.0
top_height = 20.0
chamfer_size = 1.0
mount_hole_diameter = 5.0
mount_hole_offset = 20.0
slot_width = 8.0
slot_depth = 4.0
slot_length = 30.0

total_height = base_height + step_height + top_height

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            l1 = Line((0, 0), (base_radius, 0))
            l2 = Line(l1 @ 1, (base_radius, base_height))
            l3 = Line(l2 @ 1, (step_radius, base_height))
            l4 = Line(l3 @ 1, (step_radius, base_height + step_height))
            l5 = Line(l4 @ 1, (top_radius, base_height + step_height))
            l6 = Line(l5 @ 1, (top_radius, total_height))
            l7 = Line(l6 @ 1, (0, total_height))
            l8 = Line(l7 @ 1, (0, 0))
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part

chamfer_edges = [e for e in solid_body.edges() if abs(e.center().Z - base_height) < 0.1 or abs(e.center().Z - (base_height + step_height)) < 0.1]
solid_body = chamfer(chamfer_edges, chamfer_size)

for x, y in [(0, mount_hole_offset), (0, -mount_hole_offset)]:
    solid_body = solid_body - Pos(x, y, total_height / 2) * Cylinder(mount_hole_diameter / 2, total_height + 10)

slot_box = Pos(step_radius - slot_depth / 2, 0, base_height + step_height / 2) * Box(slot_depth, slot_length, slot_width)
solid_body = solid_body - slot_box

part = solid_body
part.name = "stepped_cylinder_with_holes_and_slot"
export_step(part, "output.step")