from build123d import *

plate_length = 80.0
plate_width = 50.0
plate_thickness = 8.0
boss_diameter = 30.0
boss_height = 4.0
hole_diameter = 5.0
hole_spacing = 15.0
hole_count = 5
chamfer_distance = 1.0
pocket_width = 20.0
pocket_length = 30.0
pocket_depth = 2.0

result = Box(plate_length, plate_width, plate_thickness)
result = chamfer(result.edges().filter_by(Axis.Z), chamfer_distance)

boss = Pos(0, 0, plate_thickness/2 + boss_height/2) * Cylinder(boss_diameter/2, boss_height)
result = result + boss

pocket = Pos(0, 0, plate_thickness/2 + boss_height - pocket_depth/2) * Box(pocket_length, pocket_width, pocket_depth)
result = result - pocket

hole_h = plate_thickness + boss_height + 10
for i in range(hole_count):
    x = (i - (hole_count - 1) / 2) * hole_spacing
    result = result - Pos(x, 0, 0) * Cylinder(hole_diameter/2, hole_h)

part = result
part.name = "plate_with_boss_pocket_and_holes"
export_step(part, "output.step")