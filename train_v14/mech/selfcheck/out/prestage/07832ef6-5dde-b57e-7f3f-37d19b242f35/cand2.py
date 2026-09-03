from build123d import *
import math

shaft_radius = 8.0
shaft_length = 60.0
flange_outer_radius = 38.0
flange_thickness = 20.0
slot_width = 6.0
slot_depth = 12.0
slot_count = 6
bolt_hole_diameter = 5.0
bolt_circle_radius = 20.0
bolt_count = 4
chamfer_size = 1.0

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            l1 = Line((0, 0), (shaft_radius, 0))
            l2 = Line(l1 @ 1, (shaft_radius, shaft_length))
            l3 = Line(l2 @ 1, (flange_outer_radius, shaft_length))
            l4 = Line(l3 @ 1, (flange_outer_radius, shaft_length + flange_thickness))
            l5 = Line(l4 @ 1, (0, shaft_length + flange_thickness))
            l6 = Line(l5 @ 1, (0, 0))
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part

slot_center_x = flange_outer_radius - slot_depth / 2
slot_z = shaft_length + flange_thickness / 2
for i in range(slot_count):
    angle = i * 360.0 / slot_count
    slot = Rot(0, 0, angle) * Pos(slot_center_x, 0, slot_z) * Box(slot_depth, slot_width, flange_thickness)
    solid_body = solid_body - slot

for i in range(bolt_count):
    angle = i * 360.0 / bolt_count
    px = bolt_circle_radius * math.cos(math.radians(angle))
    py = bolt_circle_radius * math.sin(math.radians(angle))
    hole = Pos(px, py, shaft_length + flange_thickness / 2) * Cylinder(bolt_hole_diameter / 2, flange_thickness)
    solid_body = solid_body - hole

part = solid_body
part.name = "shaft_with_flange"
export_step(part, "output.step")