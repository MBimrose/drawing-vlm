from build123d import *
import math

base_radius = 10.0
base_height = 10.0
twist_height = 60.0
top_width = 30.0
top_depth = 15.0
hole_diameter = 4.0
chamfer_size = 0.5
slot_width = 5.0
slot_length = 20.0

with BuildPart() as p:
    with BuildSketch() as s1:
        Circle(base_radius)
    extrude(amount=base_height)
    with BuildSketch(Plane.XY.offset(base_height)) as s2:
        Circle(base_radius)
    with BuildSketch(Plane.XY.offset(base_height + twist_height)) as s3:
        Rectangle(top_width, top_depth)
    loft()

solid_body = p.part
total_height = base_height + twist_height
solid_body = solid_body - Pos(0, 0, total_height / 2) * Cylinder(hole_diameter / 2, total_height + 20)
solid_body = solid_body - Pos(0, 0, total_height / 2) * Box(slot_width, slot_length, total_height + 20)
vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = chamfer(vertical_edges, chamfer_size)

part = solid_body
part.name = "twisted_base_with_hole_and_slot"
export_step(part, "output.step")