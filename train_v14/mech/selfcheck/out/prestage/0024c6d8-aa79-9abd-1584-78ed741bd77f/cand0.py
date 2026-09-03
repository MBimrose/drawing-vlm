from build123d import *

vertical_leg_length = 80.0
horizontal_leg_length = 70.0
leg_width = 20.0
thickness = 10.0
slot_width = 4.0
slot_length = 20.0
hole_diameter = 5.0
hole_depth = thickness - 2.0
hole_spacing = 12.0
hole_offset_from_end = 10.0
chamfer_size = 0.5

vertical = Pos(leg_width/2, vertical_leg_length/2, thickness/2) * Box(leg_width, vertical_leg_length, thickness)
horizontal = Pos(horizontal_leg_length/2, leg_width/2, thickness/2) * Box(horizontal_leg_length, leg_width, thickness)
result = vertical + horizontal

slot = Pos(leg_width/2, vertical_leg_length/2, thickness/2) * Box(slot_width, slot_length, thickness)
result = result - slot

for i in range(4):
    x = hole_offset_from_end + i * hole_spacing
    y = leg_width / 2
    hole = Pos(x, y, thickness - hole_depth/2) * Cylinder(hole_diameter/2, hole_depth)
    result = result - hole

result = chamfer(result.edges().filter_by(Axis.Z), chamfer_size)

part = result
part.name = "L_Bracket"
export_step(part, "output.step")