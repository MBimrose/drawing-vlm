from build123d import *
import math

outer_radius = 40.0
wall_thickness = 4.0
height = 30.0
rim_height = 5.0
rim_thickness = 2.0
vent_slot_width = 4.0
vent_slot_height = 12.0
vent_slot_count = 6
chamfer_size = 1.0

inner_radius = outer_radius - wall_thickness
vent_depth = wall_thickness + 1.0

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            l1 = Line((0, 0), (outer_radius, 0))
            l2 = Line(l1 @ 1, (outer_radius, height - rim_height))
            l3 = Line(l2 @ 1, (outer_radius + rim_thickness, height - rim_height))
            l4 = Line(l3 @ 1, (outer_radius + rim_thickness, height))
            l5 = Line(l4 @ 1, (0, height))
            l6 = Line(l5 @ 1, (0, 0))
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part
solid_body = solid_body - Pos(0, 0, height / 2) * Cylinder(inner_radius, height)

for i in range(vent_slot_count):
    angle = i * 360.0 / vent_slot_count
    slot = Rot(0, 0, angle) * Pos(outer_radius - vent_depth / 2, 0, 0) * Box(vent_depth, vent_slot_width, height)
    solid_body = solid_body - slot

bottom_face = solid_body.faces().sort_by(Axis.Z)[0]
solid_body = chamfer(bottom_face.edges(), chamfer_size)

part = solid_body
part.name = "vented_cup"
export_step(part, "output.step")