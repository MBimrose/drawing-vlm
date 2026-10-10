from build123d import *
import math

outer_radius = 45.0
wall_thickness = 5.0
inner_radius = outer_radius - wall_thickness
height = 30.0
lip_height = 5.0
lip_thickness = 1.0
slot_width = 4.0
slot_depth = wall_thickness + 0.5
slot_count = 6
central_hole_diameter = 10.0
chamfer_size = 0.5

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            l1 = Line((inner_radius, 0), (inner_radius, height - lip_height))
            l2 = Line(l1@1, (outer_radius, height - lip_height))
            l3 = Line(l2@1, (outer_radius + lip_thickness, height))
            l4 = Line(l3@1, (outer_radius + lip_thickness, 0))
            l5 = Line(l4@1, (inner_radius, 0))
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part

for i in range(slot_count):
    angle = i * 360.0 / slot_count
    slot = Rot(0, 0, angle) * Pos(outer_radius - slot_depth / 2, 0, 0) * Box(slot_depth, slot_width, height)
    solid_body = solid_body - slot

solid_body = solid_body - Cylinder(central_hole_diameter / 2, height * 2)

top_edges = solid_body.edges().filter_by(Axis.Z).sort_by(Axis.Z)[-1:]
solid_body = chamfer(top_edges, chamfer_size)

part = solid_body
part.name = "revolved_cup_with_slots"
export_step(part, "output.step")