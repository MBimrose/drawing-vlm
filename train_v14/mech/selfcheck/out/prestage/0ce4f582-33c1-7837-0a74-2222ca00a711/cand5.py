from build123d import *
import math

outer_diameter = 80.0
inner_diameter = 30.0
thickness = 20.0
split_gap = 2.0
pocket_depth = 5.0
pocket_margin = 5.0
countersink_diameter = 8.5
countersink_angle = 82.0
countersink_depth = 4.0
chamfer_size = 0.8
rib_width = 4.0
rib_height = 6.0
rib_count = 4

outer_radius = outer_diameter / 2.0
inner_radius = inner_diameter / 2.0
pocket_radius = inner_radius + pocket_margin
hole_offset_radius = (inner_radius + outer_radius) / 2.0

with BuildPart() as p:
    with BuildSketch() as s:
        Circle(outer_radius)
        Circle(inner_radius, mode=Mode.SUBTRACT)
    extrude(amount=thickness)

solid_body = p.part
split_box = Pos(0, outer_radius, 0) * Box(split_gap, thickness * 1.2, outer_diameter)
solid_body = solid_body - split_box
pocket_cyl = Pos(0, 0, thickness - pocket_depth / 2) * Cylinder(pocket_radius, pocket_depth)
solid_body = solid_body - pocket_cyl

for i in range(2):
    a = math.radians(i * 180.0)
    px = hole_offset_radius * math.cos(a)
    py = hole_offset_radius * math.sin(a)
    csk = Pos(px, py, thickness) * CounterSinkHole(countersink_diameter / 2, countersink_depth / 2, countersink_angle)
    solid_body = solid_body - csk

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = chamfer(top_face.edges(), chamfer_size)

for i in range(rib_count):
    a = math.radians(i * 360.0 / rib_count)
    rib = Rot(0, 0, a) * Pos(inner_radius + rib_height / 2.0, 0, thickness / 2) * Box(rib_height, rib_width, thickness)
    solid_body = solid_body + rib

part = solid_body
part.name = "split_ring_with_ribs"
export_step(part, "output.step")