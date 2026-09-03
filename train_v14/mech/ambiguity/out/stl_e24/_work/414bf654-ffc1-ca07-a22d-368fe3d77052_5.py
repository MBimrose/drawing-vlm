from build123d import *
import math

outer_radius = 20.0
wall_thickness = 2.0
length = 70.0
central_hole_diameter = 10.0
slot_width = 2.0
slot_depth = 5.0
slot_count = 6
slot_angle = 360.0 / slot_count
chamfer_size = 0.5

with BuildPart() as p:
    with BuildSketch() as s:
        Circle(outer_radius)
    extrude(amount=length)

solid_body = p.part
top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[top_face])

solid_body = solid_body - Cylinder(central_hole_diameter/2, length)

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
top_edges = top_face.edges()
solid_body = chamfer(top_edges, chamfer_size)

for i in range(slot_count):
    angle = i * slot_angle
    slot = Box(slot_width, length, slot_depth)
    slot = Rot(0, 0, angle) * Pos(outer_radius - wall_thickness/2, 0, slot_depth/2) * slot
    solid_body = solid_body - slot

part = solid_body
part.name = "hollow_cylinder_with_slots"
export_step(part, "output.step")