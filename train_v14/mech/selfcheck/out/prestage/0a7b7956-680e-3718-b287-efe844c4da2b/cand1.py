from build123d import *

lever_length = 80.0
lever_width = 20.0
lever_thickness = 10.0
flange_length = 30.0
flange_width = 30.0
flange_thickness = lever_thickness
groove_width = 8.0
groove_depth = 4.0
groove_length = 50.0
groove_offset = 5.0
hole_diameter = 6.0
hole_spacing = 20.0
hole_offset = 10.0
pivot_hole_diameter = 10.0
pivot_hole_offset = 6.0

base = Pos(lever_length/2, 0, 0) * Box(lever_length, lever_width, lever_thickness)
flange = Pos(-flange_length/2, 0, 0) * Box(flange_length, flange_width, flange_thickness)
result = base + flange

groove_center_x = -flange_length/2 + groove_offset + groove_length/2
groove = Pos(groove_center_x, 0, lever_thickness/2 - groove_depth/2) * Box(groove_length, groove_width, groove_depth)
result = result - groove

for x, y in [(-flange_length/2 + hole_offset, 0), (-flange_length/2 + hole_offset + hole_spacing, 0)]:
    result = result - Pos(x, y, 0) * Cylinder(hole_diameter/2, lever_thickness * 2)

pivot_x = lever_length - pivot_hole_offset
result = result - Pos(pivot_x, 0, 0) * Cylinder(pivot_hole_diameter/2, lever_thickness * 2)

part = result
part.name = "lever_with_flange"
export_step(part, "output.step")