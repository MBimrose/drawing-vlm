from build123d import *

base_length = 80.0
base_width = 50.0
base_thickness = 8.0
lip_height = 3.0
lip_thickness = 2.0
notch_width = 6.0
notch_depth = 8.0
hole_diameter = 4.0
countersink_diameter = 8.0
countersink_angle = 90.0
chamfer_size = 1.0

base = Pos(0, 0, base_thickness/2) * Box(base_length, base_width, base_thickness)
lip_outer = Pos(0, 0, base_thickness) * Box(base_length, base_width, lip_height)
lip_inner = Pos(0, 0, base_thickness) * Box(base_length - 2*lip_thickness, base_width - 2*lip_thickness, lip_height)
lip = lip_outer - lip_inner
notch = Pos(base_length/4, base_width/2 - notch_depth/2, 0) * Box(notch_width, notch_depth, base_thickness)

result = base + lip - notch

hole = Pos(base_length/4, base_width/4, base_thickness) * CounterSinkHole(hole_diameter/2, countersink_diameter/2, base_thickness, countersink_angle)
result = result - hole

result = chamfer(result.edges().filter_by(Axis.Z), chamfer_size)

part = result
part.name = "base_with_lip_notch_and_hole"
export_step(part, "output.step")