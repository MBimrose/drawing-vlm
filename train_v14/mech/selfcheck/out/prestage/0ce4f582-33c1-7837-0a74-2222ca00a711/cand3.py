from build123d import *
import math

outer_diameter = 80.0
inner_diameter = 30.0
thickness = 20.0
tab_width = 15.0
tab_height = 10.0
hole_diameter = 8.5
countersink_angle = 82.0
countersink_depth = 4.0
chamfer_size = 1.0
rib_width = 10.0
rib_height = 5.0
slot_width = 5.0
slot_length = 30.0

with BuildPart() as p:
    with BuildSketch() as s:
        Circle(outer_diameter / 2)
        Circle(inner_diameter / 2, mode=Mode.SUBTRACT)
        Rectangle(tab_width, tab_height)
    extrude(amount=thickness)

solid_body = p.part

rib = Pos(0, outer_diameter / 4, thickness / 2) * Box(rib_width, rib_height, thickness)
solid_body = solid_body + rib

slot = Pos(0, 0, thickness / 2) * Box(slot_width, slot_length, thickness)
solid_body = solid_body - slot

hole_spacing = outer_diameter / 3
for i in range(2):
    x = (i - 0.5) * hole_spacing
    hole = Pos(x, 0, thickness) * CounterSinkHole(hole_diameter / 2, countersink_depth / 2, thickness, countersink_angle)
    solid_body = solid_body - hole

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
top_edges = top_face.edges()
solid_body = chamfer(top_edges, chamfer_size)

part = solid_body
part.name = "flanged_disc_with_rib"
export_step(part, "output.step")