from build123d import *
import math

base_radius = 40.0
base_height = 25.0
top_radius = 30.0
top_height = 30.0
slot_width = 5.0
slot_depth = 10.0
slot_count = 12
chamfer_size = 2.0

with BuildPart() as p:
    with BuildSketch() as s1:
        RegularPolygon(base_radius, 12)
    extrude(amount=base_height)
    with BuildSketch(Plane.XY.offset(base_height)) as s2:
        RegularPolygon(top_radius, 6)
    extrude(amount=top_height)

solid_body = p.part

for i in range(slot_count):
    angle = math.radians(i * 360.0 / slot_count)
    px = (base_radius - slot_depth / 2) * math.cos(angle)
    py = (base_radius - slot_depth / 2) * math.sin(angle)
    slot = Pos(px, py, base_height / 2) * Rot(0, 0, math.degrees(angle)) * Box(slot_width, slot_depth, base_height)
    solid_body = solid_body - slot

bottom_face = solid_body.faces().sort_by(Axis.Z)[0]
bottom_edges = bottom_face.edges()
solid_body = chamfer(bottom_edges, chamfer_size)

part = solid_body
part.name = "stepped_polygon_with_slots"
export_step(part, "output.step")