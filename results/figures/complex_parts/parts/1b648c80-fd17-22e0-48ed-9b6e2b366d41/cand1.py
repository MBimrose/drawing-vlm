from build123d import *

outer_diameter = 40.0
inner_diameter = 20.0
coupler_length = 70.0
shoulder_length = 15.0
shoulder_diameter = 30.0
keyway_width = 6.0
keyway_depth = 4.0
chamfer_size = 2.0
hole_diameter = 4.0
hole_offset = 10.0
slot_width = 8.0
slot_length = 20.0
slot_depth = 5.0

outer_radius = outer_diameter / 2.0
inner_radius = inner_diameter / 2.0
shoulder_radius = shoulder_diameter / 2.0

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            l1 = Line((0, 0), (outer_radius, 0))
            l2 = Line(l1 @ 1, (outer_radius, shoulder_length))
            l3 = Line(l2 @ 1, (shoulder_radius, shoulder_length))
            l4 = Line(l3 @ 1, (shoulder_radius, coupler_length - shoulder_length))
            l5 = Line(l4 @ 1, (outer_radius, coupler_length - shoulder_length))
            l6 = Line(l5 @ 1, (outer_radius, coupler_length))
            l7 = Line(l6 @ 1, (0, coupler_length))
            l8 = Line(l7 @ 1, (0, 0))
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part
solid_body = solid_body - Pos(0, 0, coupler_length / 2) * Cylinder(inner_radius, coupler_length)
solid_body = solid_body - Pos(inner_radius - keyway_depth / 2.0, 0, coupler_length / 2) * Box(keyway_depth, keyway_width, coupler_length)
bottom_face = solid_body.faces().sort_by(Axis.Z)[0]
solid_body = chamfer(bottom_face.edges(), chamfer_size)
solid_body = solid_body - Pos(outer_radius, 0, coupler_length / 2) * Rot(0, 90, 0) * Cylinder(hole_diameter / 2, outer_diameter)
solid_body = solid_body - Pos(-outer_radius, 0, coupler_length / 2) * Rot(0, 90, 0) * Cylinder(hole_diameter / 2, outer_diameter)
solid_body = solid_body - Pos(0, 0, coupler_length - slot_depth / 2) * Box(slot_width, slot_length, slot_depth)

part = solid_body
part.name = "coupler"
export_step(part, "output.step")