from build123d import *

total_length = 80.0
base_radius = 25.0
top_radius = 10.0
central_hole_diameter = 8.0
mount_hole_diameter = 4.0
mount_hole_spacing = 30.0
slot_width = 6.0
slot_length = 20.0
slot_depth = 4.0
chamfer_distance = 0.5

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            l1 = Line((0, 0), (base_radius, 0))
            l2 = Line(l1 @ 1, (top_radius, total_length))
            l3 = Line(l2 @ 1, (0, total_length))
            l4 = Line(l3 @ 1, (0, 0))
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part
solid_body = solid_body - Pos(0, 0, total_length / 2) * Cylinder(central_hole_diameter / 2, total_length)

for x in [-mount_hole_spacing / 2, mount_hole_spacing / 2]:
    solid_body = solid_body - Pos(x, 0, total_length / 2) * Rot(90, 0, 0) * Cylinder(mount_hole_diameter / 2, total_length)

slot_box = Pos(base_radius - slot_depth / 2, 0, total_length / 2) * Box(slot_depth, slot_length, slot_width)
solid_body = solid_body - slot_box

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
top_edges = top_face.edges()
solid_body = chamfer(top_edges, chamfer_distance)

part = solid_body
part.name = "tapered_cylinder_with_holes_and_slot"
export_step(part, "output.step")