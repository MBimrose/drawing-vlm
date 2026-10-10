from build123d import *
import math

outer_radius = 40.0
wall_thickness = 6.0
height = 30.0
fillet_radius = 2.0
pocket_radius = 20.0
pocket_depth = 4.0
slot_width = 4.0
slot_height = 15.0
slot_count = 6

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            l1 = Line((outer_radius, 0), (outer_radius, height - fillet_radius))
            l2 = ThreePointArc(l1 @ 1, (outer_radius + fillet_radius, height - fillet_radius), (outer_radius + fillet_radius, height))
            l3 = Line(l2 @ 1, (outer_radius + wall_thickness, height))
            l4 = Line(l3 @ 1, (outer_radius + wall_thickness, 0))
            l5 = Line(l4 @ 1, (outer_radius, 0))
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part

pocket = Pos(0, 0, height - pocket_depth / 2) * Cylinder(pocket_radius, pocket_depth)
solid_body = solid_body - pocket

for i in range(slot_count):
    angle = i * 360.0 / slot_count
    slot = Rot(0, 0, angle) * Pos(outer_radius + wall_thickness / 2, 0, slot_height / 2) * Box(wall_thickness + 0.2, slot_width, slot_height)
    solid_body = solid_body - slot

part = solid_body
part.name = "revolved_cup_with_pocket_and_slots"
export_step(part, "output.step")