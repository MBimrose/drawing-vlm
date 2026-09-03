from build123d import *
import math

outer_radius = 20.0
wall_thickness = 2.0
inner_radius = outer_radius - wall_thickness
total_length = 70.0
central_hole_radius = 5.0
slot_width = 2.0
slot_length = 12.0
slot_angle = 45.0
chamfer_distance = 0.5

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            l1 = Line((inner_radius, 0), (outer_radius, 0))
            l2 = Line(l1@1, (outer_radius, total_length))
            l3 = Line(l2@1, (inner_radius, total_length))
            l4 = Line(l3@1, (inner_radius, 0))
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part
solid_body = solid_body - Cylinder(central_hole_radius, total_length)

for angle in [slot_angle, -slot_angle, 180 - slot_angle, -(180 - slot_angle)]:
    slot = Rot(0, 0, angle) * Pos(outer_radius - wall_thickness/2, 0, 0) * Rot(0, 90, 0) * Box(slot_width, slot_length, wall_thickness * 2)
    solid_body = solid_body - slot

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
top_edges = top_face.edges()
solid_body = chamfer(top_edges, chamfer_distance)

part = solid_body
part.name = "thin_walled_tube_with_slots"
export_step(part, "output.step")