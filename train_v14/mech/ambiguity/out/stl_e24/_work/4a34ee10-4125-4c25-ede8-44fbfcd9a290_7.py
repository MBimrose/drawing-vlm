from build123d import *
import math

outer_radius = 45.0
inner_radius = 30.0
thickness = 12.0
slot_width = 4.0
slot_depth = 6.0
slot_count = 4
hole_diameter = 4.0
hole_count = 4
chamfer_size = 0.8

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            l1 = Line((inner_radius, 0), (outer_radius, 0))
            l2 = Line(l1@1, (outer_radius, thickness))
            l3 = Line(l2@1, (inner_radius, thickness))
            l4 = Line(l3@1, (inner_radius, 0))
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part

slot_radius = outer_radius - slot_depth / 2
for i in range(slot_count):
    angle = math.radians(i * 360.0 / slot_count)
    px = slot_radius * math.cos(angle)
    py = slot_radius * math.sin(angle)
    slot = Pos(px, py, 0) * Box(slot_depth, slot_width, thickness)
    solid_body = solid_body - slot

hole_radius = (inner_radius + outer_radius) / 2
for i in range(hole_count):
    angle = math.radians(45 + i * 360.0 / hole_count)
    px = hole_radius * math.cos(angle)
    py = hole_radius * math.sin(angle)
    hole = Pos(px, py, 0) * Cylinder(hole_diameter / 2, thickness * 2)
    solid_body = solid_body - hole

solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_size)

part = solid_body
part.name = "ring_with_slots_and_holes"
export_step(part, "output.step")