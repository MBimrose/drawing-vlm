from build123d import *

leg_length_horizontal = 70.0
leg_length_vertical = 80.0
leg_width = 20.0
thickness = 10.0
slot_width = 4.0
slot_length = 20.0
hole_diameter = 5.0
hole_depth = 8.0
hole_spacing = 12.0
hole_count = 4
chamfer_size = 0.5

horizontal = Pos(leg_length_horizontal/2, leg_width/2, 0) * Box(leg_length_horizontal, leg_width, thickness)
vertical = Pos(leg_width/2, leg_length_vertical/2, 0) * Box(leg_width, leg_length_vertical, thickness)
base = horizontal + vertical

slot = Pos(leg_width/2, leg_length_vertical/2, 0) * Box(slot_width, slot_length, thickness)
base = base - slot

for i in range(hole_count):
    x = leg_length_horizontal/2 + (i - (hole_count-1)/2) * hole_spacing
    y = leg_width/2
    hole = Pos(x, y, thickness/2 - hole_depth/2) * Cylinder(hole_diameter/2, hole_depth)
    base = base - hole

base = chamfer(base.edges().filter_by(Axis.Z), chamfer_size)

part = base
part.name = "L_Bracket"
export_step(part, "output.step")