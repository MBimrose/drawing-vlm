from build123d import *
import math

outer_radius = 20.0
wall_thickness = 2.0
inner_radius = outer_radius - wall_thickness
body_length = 70.0
slot_width = 5.0
slot_depth = wall_thickness
num_slots = 6
slot_angle = 360.0 / num_slots
chamfer_size = 0.5
central_hole_diameter = 10.0

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            l1 = Line((inner_radius, 0), (outer_radius, 0))
            l2 = Line(l1 @ 1, (outer_radius, body_length))
            l3 = Line(l2 @ 1, (inner_radius, body_length))
            l4 = Line(l3 @ 1, (inner_radius, 0))
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part
solid_body = solid_body - Cylinder(central_hole_diameter / 2, body_length)

slot_box = Pos(outer_radius - slot_depth / 2, 0, 0) * Box(slot_depth, body_length, slot_width)
for i in range(num_slots):
    angle = i * slot_angle
    rotated_slot = Rot(0, angle, 0) * slot_box
    solid_body = solid_body - rotated_slot

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
top_edges = top_face.edges()
solid_body = chamfer(top_edges, chamfer_size)

part = solid_body
part.name = "hollow_cylinder_with_slots"
export_step(part, "output.step")