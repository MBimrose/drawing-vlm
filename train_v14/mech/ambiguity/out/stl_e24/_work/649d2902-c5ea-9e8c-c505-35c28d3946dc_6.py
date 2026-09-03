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
rib_width = 4.0
rib_length = 20.0
rib_height = 4.0
rib_spacing = 15.0
pocket_length = 30.0
pocket_width = 20.0
pocket_depth = 4.0

result = Box(plate_length, plate_width, plate_thickness)
result = result + Pos(0, 0, plate_thickness/2 + boss_height/2) * Cylinder(boss_diameter/2, boss_height)

for i in range(hole_count):
    x = (i - (hole_count-1)/2) * hole_spacing
    result = result - Pos(x, 0, 0) * Cylinder(hole_diameter/2, plate_thickness + boss_height + 10)

result = result - Pos(0, 0, plate_thickness/2 + boss_height - pocket_depth/2) * Box(pocket_length, pocket_width, pocket_depth)

result = chamfer(result.edges().filter_by(Axis.Z), chamfer_distance)

for i in range(2):
    y = (i - 0.5) * rib_spacing
    result = result + Pos(0, y, plate_thickness/2 + rib_height/2) * Box(rib_length, rib_width, rib_height)

part = result
part.name = "plate_with_boss_holes_pocket_ribs"
export_step(part, "output.step")