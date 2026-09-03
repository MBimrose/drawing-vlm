from build123d import *

knob_diameter = 60.0
knob_height = 15.0
rib_count = 12
rib_width = 2.0
rib_height = 4.0
rib_thickness = 1.0
blind_hole_diameter = 10.0
blind_hole_depth = 8.0

base = Pos(0, 0, knob_height / 2) * Cylinder(knob_diameter / 2, knob_height)
rib = Pos(knob_diameter / 2 - rib_width / 2, 0, knob_height + rib_thickness / 2) * Box(rib_width, rib_height, rib_thickness)

ribs = rib
for i in range(1, rib_count):
    angle = i * 360.0 / rib_count
    ribs = ribs + Rot(0, 0, angle) * rib

combined = base + ribs
hole = Pos(0, 0, knob_height - blind_hole_depth / 2) * Cylinder(blind_hole_diameter / 2, blind_hole_depth)
part = combined - hole
part.name = "knob_with_ribs"
export_step(part, "output.step")