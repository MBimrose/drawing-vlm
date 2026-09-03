from build123d import *

vertical_height = 70.0
horizontal_length = 80.0
thickness = 10.0
chamfer_size = 1.0
hole_diameter = 5.0
hole_offset_from_end = 20.0
hole_spacing = 40.0
notch_width = 6.0
notch_depth = 5.0

vertical = Pos(thickness/2, vertical_height/2, thickness/2) * Box(thickness, vertical_height, thickness)
horizontal = Pos(horizontal_length/2, vertical_height - thickness/2, thickness/2) * Box(horizontal_length, thickness, thickness)
result = vertical + horizontal

notch = Pos(horizontal_length/2, vertical_height - notch_depth/2, thickness/2) * Box(notch_width, notch_depth, thickness)
result = result - notch

for x, z in [(hole_offset_from_end, thickness/2), (hole_offset_from_end + hole_spacing, thickness/2)]:
    hole = Pos(x, vertical_height, z) * Rot(90, 0, 0) * Cylinder(hole_diameter/2, 200)
    result = result - hole

edges = result.edges()
min_x = min(e.center().X for e in edges)
min_y = min(e.center().Y for e in edges)
target_edges = [e for e in edges if abs(e.center().X - min_x) < 0.01 and abs(e.center().Y - min_y) < 0.01]
result = chamfer(target_edges, chamfer_size)

part = result
part.name = "L_Bracket"
export_step(part, "output.step")