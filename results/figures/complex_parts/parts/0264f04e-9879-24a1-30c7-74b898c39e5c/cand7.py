from build123d import *

base_radius = 30.0
base_height = 15.0
middle_radius = 20.0
middle_height = 15.0
top_radius = 12.0
top_height = 20.0
total_height = base_height + middle_height + top_height
slot_width = 8.0
slot_depth = 6.0
slot_height = 12.0
mount_hole_dia = 5.0
mount_hole_spacing = 40.0
chamfer_size = 1.0

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            l1 = Line((0, 0), (base_radius, 0))
            l2 = Line(l1 @ 1, (base_radius, base_height))
            l3 = Line(l2 @ 1, (middle_radius, base_height))
            l4 = Line(l3 @ 1, (middle_radius, base_height + middle_height))
            l5 = Line(l4 @ 1, (top_radius, base_height + middle_height))
            l6 = Line(l5 @ 1, (top_radius, total_height))
            l7 = Line(l6 @ 1, (0, total_height))
            l8 = Line(l7 @ 1, (0, 0))
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part
solid_body = chamfer(solid_body.edges(), chamfer_size)

slot_box = Pos(top_radius - slot_depth / 2, 0, total_height - slot_height / 2) * Box(slot_depth, slot_width, slot_height)
solid_body = solid_body - slot_box

for y in [-mount_hole_spacing / 2, mount_hole_spacing / 2]:
    hole = Pos(0, y, total_height / 2) * Cylinder(mount_hole_dia / 2, total_height + 10)
    solid_body = solid_body - hole

part = solid_body
part.name = "stepped_knob"
export_step(part, "output.step")