from build123d import *
import math

outer_diameter = 40.0
wall_thickness = 2.0
length = 70.0
groove_width = 5.0
groove_depth = 1.5
central_hole_diameter = 8.0
side_hole_diameter = 6.0
side_hole_offset = 20.0
chamfer_size = 0.5
slot_width = 2.0
slot_length = 10.0
slot_depth = 1.0
slot_count = 4
slot_angle = 360.0 / slot_count

with BuildPart() as p:
    with BuildSketch() as s:
        Circle(outer_diameter / 2)
    extrude(amount=length)

solid_body = p.part
top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[top_face])

groove_radius = (outer_diameter / 2) - wall_thickness - groove_depth
groove_cyl = Pos(0, 0, length / 2 - groove_width / 2) * Cylinder(groove_radius, groove_width)
solid_body = solid_body - groove_cyl

central_hole = Rot(90, 0, 0) * Cylinder(central_hole_diameter / 2, length)
solid_body = solid_body - central_hole

for y_off in [side_hole_offset, -side_hole_offset]:
    side_hole = Pos(0, y_off, 0) * Rot(90, 0, 0) * Cylinder(side_hole_diameter / 2, length)
    solid_body = solid_body - side_hole

for i in range(slot_count):
    angle = i * slot_angle
    slot = Rot(0, angle, 0) * Pos(outer_diameter / 2 - wall_thickness - slot_depth / 2, 0, 0) * Box(slot_width, slot_length, slot_depth)
    solid_body = solid_body - slot

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
top_edges = top_face.edges()
solid_body = chamfer(top_edges, chamfer_size)

part = solid_body
part.name = "hollow_cylinder_with_grooves_and_slots"
export_step(part, "output.step")