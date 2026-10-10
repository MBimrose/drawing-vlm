from build123d import *

outer_diameter = 40.0
inner_diameter = 20.0
length = 70.0
step1_length = 10.0
step2_length = 15.0
step1_diameter = 30.0
step2_diameter = 30.0
chamfer_size = 2.0
set_screw_diameter = 4.0
set_screw_offset = 35.0
slot_width = 6.0
slot_depth = 5.0

outer_radius = outer_diameter / 2.0
inner_radius = inner_diameter / 2.0
step1_radius = step1_diameter / 2.0
step2_radius = step2_diameter / 2.0

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            l1 = Line((0, 0), (outer_radius, 0))
            l2 = Line(l1 @ 1, (outer_radius, step1_length))
            l3 = Line(l2 @ 1, (step1_radius, step1_length))
            l4 = Line(l3 @ 1, (step1_radius, step1_length + step2_length))
            l5 = Line(l4 @ 1, (outer_radius, step1_length + step2_length))
            l6 = Line(l5 @ 1, (outer_radius, length))
            l7 = Line(l6 @ 1, (0, length))
            l8 = Line(l7 @ 1, (0, 0))
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part
solid_body = solid_body - Pos(0, 0, length / 2) * Cylinder(inner_radius, length)

bottom_face = solid_body.faces().sort_by(Axis.Z)[0]
solid_body = chamfer(bottom_face.edges(), chamfer_size)

set_screw = Pos(0, 0, set_screw_offset) * Rot(0, 90, 0) * Cylinder(set_screw_diameter / 2.0, outer_diameter)
solid_body = solid_body - set_screw

slot = Pos(inner_radius + slot_depth / 2.0, 0, length / 2.0) * Box(slot_depth, slot_width, length)
solid_body = solid_body - slot

part = solid_body
part.name = "stepped_shaft_with_slot"
export_step(part, "output.step")