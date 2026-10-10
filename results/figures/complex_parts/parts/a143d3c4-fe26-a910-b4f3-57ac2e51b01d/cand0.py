from build123d import *
import math

base_diameter = 30.0
top_diameter = 80.0
cone_height = 40.0
flange_thickness = 8.0
slot_width = 10.0
slot_height = 30.0
slot_offset = 5.0
hole_diameter = 5.0
hole_count = 6
hole_circle_radius = 30.0
chamfer_size = 1.0

with BuildPart() as p:
    with BuildSketch() as s1:
        Circle(base_diameter / 2)
    with BuildSketch(Plane.XY.offset(cone_height)) as s2:
        Circle(top_diameter / 2)
    loft()
    with BuildSketch(Plane.XY.offset(cone_height)) as s3:
        Circle(top_diameter / 2)
    extrude(amount=flange_thickness)

solid_body = p.part

slot_box = Pos(base_diameter / 2 - slot_width / 2, 0, slot_offset) * Box(slot_width, top_diameter, slot_height)
solid_body = solid_body - slot_box

for i in range(hole_count):
    angle = math.radians(i * 360.0 / hole_count)
    px = hole_circle_radius * math.cos(angle)
    py = hole_circle_radius * math.sin(angle)
    solid_body = solid_body - Pos(px, py, cone_height + flange_thickness / 2) * Cylinder(hole_diameter / 2, flange_thickness + 20)

vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = chamfer(vertical_edges, chamfer_size)

part = solid_body
part.name = "conical_flange_with_slot"
export_step(part, "output.step")