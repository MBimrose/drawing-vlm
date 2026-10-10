from build123d import *

plate_width = 80.0
plate_depth = 80.0
plate_thickness = 15.0
boss_diameter = 50.0
boss_height = 60.0
bore_diameter = 30.0
corner_hole_diameter = 8.0
corner_hole_offset = 10.0
chamfer_size = 5.0
boss_chamfer = 1.0

plate = Box(plate_width, plate_depth, plate_thickness)
boss = Pos(0, 0, plate_thickness/2 + boss_height/2) * Cylinder(boss_diameter/2, boss_height)
result = plate + boss

bore = Pos(0, 0, plate_thickness/2 + boss_height/2) * Cylinder(bore_diameter/2, plate_thickness + boss_height + 20)
result = result - bore

corner_x = plate_width/2 - corner_hole_offset - corner_hole_diameter/2
corner_y = plate_depth/2 - corner_hole_offset - corner_hole_diameter/2
for cx, cy in [(corner_x, corner_y), (-corner_x, corner_y), (-corner_x, -corner_y), (corner_x, -corner_y)]:
    result = result - Pos(cx, cy, 0) * Cylinder(corner_hole_diameter/2, plate_thickness + 20)

result = chamfer(result.edges().filter_by(Axis.Z), chamfer_size)
result = chamfer(result.edges().filter_by(Axis.Z, reverse=True), boss_chamfer)

part = result
part.name = "plate_with_boss_and_holes"
export_step(part, "output.step")