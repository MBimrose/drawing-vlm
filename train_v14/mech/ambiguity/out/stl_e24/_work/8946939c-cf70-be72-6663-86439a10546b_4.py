from build123d import *

vertical_leg_length = 60.0
horizontal_leg_length = 80.0
thickness = 10.0
depth = 10.0
chamfer_size = 1.0
hole_diameter = 8.5
hole_spacing = 12.0
hole_count = 5

vertical = Pos(thickness/2, vertical_leg_length/2, 0) * Box(thickness, vertical_leg_length, depth)
horizontal = Pos(horizontal_leg_length/2, thickness/2, 0) * Box(horizontal_leg_length, thickness, depth)
result = vertical + horizontal

x_face = result.faces().sort_by(Axis.X)[-1]
result = chamfer(x_face.edges(), chamfer_size)

for i in range(hole_count):
    x = horizontal_leg_length/2 + (i - (hole_count-1)/2) * hole_spacing
    y = thickness/2
    result = result - Pos(x, y, 0) * Cylinder(hole_diameter/2, depth + 2)

part = result
part.name = "L_Bracket"
export_step(part, "output.step")