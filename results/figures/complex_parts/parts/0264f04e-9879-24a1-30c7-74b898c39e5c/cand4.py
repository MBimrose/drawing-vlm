from build123d import *

base_radius = 30.0
base_height = 15.0
step1_radius = 20.0
step1_height = 15.0
step2_radius = 12.0
step2_height = 20.0
fillet_radius = 2.0
mount_hole_dia = 5.0
mount_hole_spacing = 40.0
central_hole_dia = 10.0
slot_width = 10.0
slot_length = 30.0

total_height = base_height + step1_height + step2_height

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            l1 = Line((0, 0), (base_radius, 0))
            l2 = Line(l1 @ 1, (base_radius, base_height))
            l3 = Line(l2 @ 1, (step1_radius, base_height))
            l4 = Line(l3 @ 1, (step1_radius, base_height + step1_height))
            l5 = Line(l4 @ 1, (step2_radius, base_height + step1_height))
            l6 = Line(l5 @ 1, (step2_radius, total_height))
            l7 = Line(l6 @ 1, (0, total_height))
            l8 = Line(l7 @ 1, (0, 0))
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part
solid_body = fillet(solid_body.edges(), fillet_radius)

for y in [-mount_hole_spacing/2, mount_hole_spacing/2]:
    solid_body = solid_body - Pos(0, y, total_height/2) * Cylinder(mount_hole_dia/2, total_height + 10)

solid_body = solid_body - Pos(0, 0, total_height/2) * Cylinder(central_hole_dia/2, total_height + 10)

solid_body = solid_body - Pos(0, 0, total_height - step2_height/2) * Box(slot_length, slot_width, step2_height)

part = solid_body
part.name = "stepped_cylinder_with_holes_and_slot"
export_step(part, "output.step")