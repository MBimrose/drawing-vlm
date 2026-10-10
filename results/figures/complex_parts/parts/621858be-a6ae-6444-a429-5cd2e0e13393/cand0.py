from build123d import *

outer_radius = 45
wall_thickness = 6
height = 30
recess_depth = 5
slot_width = 4
slot_depth = wall_thickness + 2
num_slots = 6
chamfer_size = 1

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            l1 = Line((outer_radius, 0), (outer_radius, height))
            l2 = Line(l1@1, (outer_radius + wall_thickness, height))
            l3 = Line(l2@1, (outer_radius + wall_thickness, 0))
            l4 = Line(l3@1, (outer_radius, 0))
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part

recess = Pos(0, 0, height - recess_depth/2) * Cylinder(outer_radius, recess_depth)
solid_body = solid_body - recess

import math
for i in range(num_slots):
    angle = i * 360.0 / num_slots
    slot = Rot(0, 0, angle) * Pos(outer_radius + wall_thickness/2, 0, 0) * Box(slot_depth, slot_width, height)
    solid_body = solid_body - slot

vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = chamfer(vertical_edges, chamfer_size)

part = solid_body
part.name = "revolved_cup_with_slots"
export_step(part, "output.step")