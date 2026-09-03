from build123d import *
import math

outer_diameter = 60.0
inner_diameter = 30.0
thickness = 12.0
slot_width = 6.0
slot_length = 20.0
fillet_radius = 2.0
rib_count = 6
rib_width = 3.0
rib_height = 2.0
hole_diameter = 5.0
hole_offset_radius = (outer_diameter/2) - 5.0

with BuildPart() as p:
    with BuildSketch() as s:
        Circle(outer_diameter/2)
        Circle(inner_diameter/2, mode=Mode.SUBTRACT)
    extrude(amount=thickness)

solid_body = p.part

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
top_edges = top_face.edges()
solid_body = fillet(top_edges, fillet_radius)

slot = Pos(outer_diameter/2 - slot_length/2, 0, thickness/2) * Box(slot_length, slot_width, thickness)
solid_body = solid_body - slot

for i in range(rib_count):
    angle = i * 360.0 / rib_count
    rib = Rot(0, 0, angle) * Pos(outer_diameter/2 - rib_height/2, 0, thickness/2) * Box(rib_width, rib_height, thickness)
    solid_body = solid_body + rib

for i in range(4):
    angle = math.radians(i * 90.0)
    px = hole_offset_radius * math.cos(angle)
    py = hole_offset_radius * math.sin(angle)
    hole = Pos(px, py, thickness/2) * Cylinder(hole_diameter/2, thickness)
    solid_body = solid_body - hole

part = solid_body
part.name = "flanged_ring_with_ribs"
export_step(part, "output.step")