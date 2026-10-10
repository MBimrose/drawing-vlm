from build123d import *

base_radius = 30.0
base_height = 15.0
step1_radius = 20.0
step1_height = 15.0
step2_radius = 12.0
step2_height = 20.0
fillet_radius = 2.0
hole_diameter = 5.0
hole_spacing = 40.0
slot_width = 6.0
slot_length = 12.0
slot_depth = 4.0

total_height = base_height + step1_height + step2_height

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            l1 = Line((0, 0), (base_radius, 0))
            l2 = Line(l1 @ 1, (base_radius, base_height))
            l3 = Line(l2 @ 1, (step1_radius, base_height))
            a1 = ThreePointArc(l3 @ 1, (step1_radius - fillet_radius, base_height + fillet_radius), (step1_radius, base_height + step1_height - fillet_radius))
            l4 = Line(a1 @ 1, (step1_radius, base_height + step1_height))
            a2 = ThreePointArc(l4 @ 1, (step2_radius + fillet_radius, base_height + step1_height + fillet_radius), (step2_radius, base_height + step1_height + step2_height - fillet_radius))
            l5 = Line(a2 @ 1, (step2_radius, total_height))
            l6 = Line(l5 @ 1, (0, total_height))
            l7 = Line(l6 @ 1, (0, 0))
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part

for y in [-hole_spacing/2, hole_spacing/2]:
    solid_body = solid_body - Pos(0, y, total_height/2) * Cylinder(hole_diameter/2, total_height + 10)

slot_box = Pos(step2_radius/2, 0, total_height - slot_depth/2) * Box(slot_width, slot_length, slot_depth)
solid_body = solid_body - slot_box

part = solid_body
part.name = "stepped_cylinder_with_holes_and_slot"
export_step(part, "output.step")