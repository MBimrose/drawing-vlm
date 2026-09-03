from build123d import *
import math

knob_diameter = 60.0
knob_height = 15.0
rib_width = 2.0
rib_height = 4.0
rib_thickness = 2.0
rib_count = 12
central_hole_diameter = 10.0
central_hole_depth = 10.0

base = Cylinder(knob_diameter / 2, knob_height)

rib_radius = knob_diameter / 2 - rib_width / 2
rib_z = knob_height / 2
rib = Box(rib_width, rib_height, rib_thickness)

ribs = Pos(rib_radius, 0, rib_z) * rib
for i in range(1, rib_count):
    angle = math.radians(i * 360.0 / rib_count)
    px = rib_radius * math.cos(angle)
    py = rib_radius * math.sin(angle)
    ribs = ribs + Pos(px, py, rib_z) * Rot(0, 0, math.degrees(angle)) * rib

result = base + ribs

hole = Pos(0, 0, knob_height / 2 - central_hole_depth / 2) * Cylinder(central_hole_diameter / 2, central_hole_depth)
result = result - hole

part = result
part.name = "knob_with_ribs"
export_step(part, "output.step")