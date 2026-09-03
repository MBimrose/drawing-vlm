from build123d import *
import math

outer_diameter = 80.0
inner_diameter = 20.0
thickness = 5.0
slot_width = 5.0
slot_length = 20.0
hole_diameter = 4.0
hole_count = 12
hole_radius = 30.0
chamfer_size = 0.5

with BuildPart() as p:
    with BuildSketch() as s:
        Circle(outer_diameter / 2)
        Circle(inner_diameter / 2, mode=Mode.SUBTRACT)
    extrude(amount=thickness)

solid_body = p.part

slot_box = Pos(0, outer_diameter / 2 - slot_length / 2, thickness / 2) * Box(slot_width, slot_length, thickness)
solid_body = solid_body - slot_box

for i in range(hole_count):
    angle = math.radians(i * 360.0 / hole_count)
    px = hole_radius * math.cos(angle)
    py = hole_radius * math.sin(angle)
    solid_body = solid_body - Pos(px, py, thickness / 2) * Cylinder(hole_diameter / 2, thickness)

vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = chamfer(vertical_edges, chamfer_size)

part = solid_body
part.name = "washer_with_slot_and_holes"
export_step(part, "output.step")