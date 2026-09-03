from build123d import *
import math

outer_radius = 30.0
inner_radius = 20.0
thickness = 12.0
keyway_width = 6.0
keyway_depth = 20.0
fillet_radius = 1.5
hole_diameter = 5.0
hole_offset = 5.0
rib_thickness = 3.0
rib_width = 6.0
rib_count = 6

with BuildPart() as p:
    with BuildSketch() as s:
        Circle(outer_radius)
        Circle(inner_radius)
    extrude(amount=thickness)

solid_body = p.part

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
top_edges = top_face.edges()
solid_body = fillet(top_edges, fillet_radius)

keyway_center_x = outer_radius - keyway_depth / 2.0
keyway = Pos(keyway_center_x, 0, thickness / 2) * Box(keyway_depth, keyway_width, thickness)
solid_body = solid_body - keyway

hole_radius = outer_radius - hole_offset
for i in range(4):
    angle = math.radians(i * 90)
    px = hole_radius * math.cos(angle)
    py = hole_radius * math.sin(angle)
    hole = Pos(px, py, thickness / 2) * Cylinder(hole_diameter / 2, thickness)
    solid_body = solid_body - hole

rib_center_x = outer_radius - rib_thickness / 2.0
for i in range(rib_count):
    angle = math.radians(i * 360 / rib_count)
    rib = Rot(0, 0, angle) * Pos(rib_center_x, 0, thickness / 2) * Box(rib_thickness, rib_width, thickness)
    solid_body = solid_body + rib

part = solid_body
part.name = "ring_with_keyway_holes_and_ribs"
export_step(part, "output.step")