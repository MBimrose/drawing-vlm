from build123d import *
import math

outer_diameter = 80.0
wall_thickness = 5.0
height = 60.0
central_hole_diameter = 20.0
slot_width = 4.0
slot_height = 12.0
slot_count = 6
chamfer_distance = 1.0

outer_radius = outer_diameter / 2.0
inner_radius = outer_radius - wall_thickness

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            l1 = Line((outer_radius, 0), (outer_radius, height - chamfer_distance))
            l2 = Line(l1 @ 1, (outer_radius - chamfer_distance, height))
            l3 = Line(l2 @ 1, (inner_radius, height))
            l4 = Line(l3 @ 1, (inner_radius, 0))
            l5 = Line(l4 @ 1, (outer_radius, 0))
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part
solid_body = solid_body - Cylinder(central_hole_diameter / 2, height + 2)

for i in range(slot_count):
    angle = i * 360.0 / slot_count
    slot = Rot(0, 0, angle) * Pos(outer_radius - wall_thickness / 2.0, 0, 0) * Box(slot_width, wall_thickness + 0.2, slot_height)
    solid_body = solid_body - slot

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
top_edges = top_face.edges()
solid_body = chamfer(top_edges, chamfer_distance)

part = solid_body
part.name = "revolved_cup_with_slots"
export_step(part, "output.step")