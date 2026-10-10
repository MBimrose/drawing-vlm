from build123d import *
import math

outer_radius = 45.0
wall_thickness = 5.0
height = 30.0
lip_height = 3.0
lip_thickness = 2.0
slot_width = 4.0
slot_depth = wall_thickness + 2.0
slot_height = 15.0
slot_count = 6
chamfer_size = 1.0

inner_radius = outer_radius - wall_thickness

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            l1 = Line((inner_radius, 0), (inner_radius, height - lip_height))
            l2 = Line(l1@1, (inner_radius + lip_thickness, height - lip_height))
            l3 = Line(l2@1, (inner_radius + lip_thickness, height))
            l4 = Line(l3@1, (outer_radius + lip_thickness, height))
            l5 = Line(l4@1, (outer_radius + lip_thickness, 0))
            l6 = Line(l5@1, (inner_radius, 0))
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part

for i in range(slot_count):
    angle = i * 360.0 / slot_count
    slot = Rot(0, 0, angle) * Pos(outer_radius - slot_depth/2, 0, slot_height/2) * Box(slot_depth, slot_width, slot_height)
    solid_body = solid_body - slot

vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = chamfer(vertical_edges, chamfer_size)

part = solid_body
part.name = "revolved_cup_with_slots"
export_step(part, "output.step")