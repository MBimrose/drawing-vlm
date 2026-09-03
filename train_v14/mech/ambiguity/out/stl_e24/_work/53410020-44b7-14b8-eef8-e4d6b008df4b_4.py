from build123d import *
import math

outer_diameter = 60.0
inner_diameter = 40.0
thickness = 12.0
fillet_radius = 2.0
slot_width = 6.0
slot_length = 20.0
slot_offset = 20.0
hole_diameter = 5.0
hole_radius = 25.0
rib_width = 3.0
rib_height = 5.0
boss_diameter = 30.0
boss_height = 5.0
groove_width = 2.0
groove_depth = 3.0
groove_count = 6

with BuildPart() as p:
    with BuildSketch() as s:
        Circle(outer_diameter / 2)
        Circle(inner_diameter / 2, mode=Mode.SUBTRACT)
    extrude(amount=thickness)

solid_body = p.part
top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = fillet(top_face.edges(), fillet_radius)

solid_body = solid_body - Pos(slot_offset, 0, thickness/2) * Box(slot_length, slot_width, thickness)

for i in range(4):
    a = math.radians(i * 90)
    solid_body = solid_body - Pos(hole_radius * math.cos(a), hole_radius * math.sin(a), thickness/2) * Cylinder(hole_diameter/2, thickness)

solid_body = solid_body + Pos(outer_diameter/2 - rib_width/2, 0, thickness/2) * Box(rib_width, rib_height, thickness)
solid_body = solid_body + Pos(0, 0, thickness/2) * Cylinder(boss_diameter/2, boss_height)

for i in range(groove_count):
    a = i * 360 / groove_count
    solid_body = solid_body - Rot(0, 0, a) * Pos(outer_diameter/2 - groove_depth/2, 0, thickness/2) * Box(groove_width, groove_depth, thickness)

part = solid_body
part.name = "ring_with_features"
export_step(part, "output.step")