from build123d import *

base_width = 80.0
base_depth = 30.0
base_thickness = 5.0
step_width = 20.0
step_height = 8.0
hole_diameter = 5.0
hole_spacing_x = 20.0
hole_spacing_y = 10.0
fillet_radius = 2.0

base = Pos(0, 0, base_thickness / 2) * Box(base_width, base_depth, base_thickness)
step = Pos(base_width / 2 - step_width / 2, 0, base_thickness + step_height / 2) * Box(step_width, base_depth, step_height)
result = base + step

hole_r = hole_diameter / 2
hole_h = base_thickness + step_height + 10.0
hole_z = (base_thickness + step_height) / 2.0

for i in range(3):
    for j in range(2):
        x = (i - 1) * hole_spacing_x
        y = (j - 0.5) * hole_spacing_y
        result = result - Pos(x, y, hole_z) * Cylinder(hole_r, hole_h)

result = fillet(result.edges(), fillet_radius)

part = result
part.name = "stepped_base_with_holes"
export_step(part, "output.step")