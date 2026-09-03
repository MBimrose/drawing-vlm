from build123d import *
import math

outer_radius = 45.0
inner_radius = 30.0
ring_height = 12.0
slot_width = 4.0
slot_depth = 6.0
num_slots = 4
chamfer_size = 1.0
hole_diameter = 4.0
hole_count = 6
boss_radius = 5.0
boss_height = 3.0

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            l1 = Line((inner_radius, 0), (outer_radius, 0))
            l2 = Line(l1@1, (outer_radius, ring_height))
            l3 = Line(l2@1, (inner_radius, ring_height))
            l4 = Line(l3@1, (inner_radius, 0))
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part
solid_body = solid_body + Pos(0, 0, ring_height/2 + boss_height/2) * Cylinder(boss_radius, boss_height)

slot_center_x = (inner_radius + outer_radius) / 2
for i in range(num_slots):
    angle = i * 360.0 / num_slots
    slot = Rot(0, 0, angle) * Pos(slot_center_x, 0, 0) * Box(slot_depth, slot_width, ring_height)
    solid_body = solid_body - slot

solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_size)

hole_radius = (inner_radius + outer_radius) / 2
for i in range(hole_count):
    angle = math.radians(i * 360.0 / hole_count)
    px = hole_radius * math.cos(angle)
    py = hole_radius * math.sin(angle)
    solid_body = solid_body - Pos(px, py, 0) * Cylinder(hole_diameter/2, ring_height + boss_height + 10)

part = solid_body
part.name = "ring_with_slots_and_holes"
export_step(part, "output.step")