from build123d import *

plate_length = 80.0
plate_width = 50.0
plate_thickness = 8.0
boss_diameter = 30.0
boss_height = 12.0
hole_diameter = 5.0
hole_spacing = 15.0
hole_count = 5
chamfer_distance = 1.0
rib_thickness = 4.0
rib_height = 6.0
rib_spacing = 20.0

result = Box(plate_length, plate_width, plate_thickness)
result = result + Pos(0, 0, -plate_thickness/2 + boss_height/2) * Cylinder(boss_diameter/2, boss_height)

rib_length = plate_length - 2 * rib_spacing
rib = Box(rib_length, rib_thickness, rib_height)
result = result + Pos(0, rib_spacing, -plate_thickness/2 + rib_height/2) * rib
result = result + Pos(0, -rib_spacing, -plate_thickness/2 + rib_height/2) * rib

hole_start_x = -((hole_count - 1) * hole_spacing) / 2
for i in range(hole_count):
    x = hole_start_x + i * hole_spacing
    result = result - Pos(x, 0, 0) * Cylinder(hole_diameter/2, 100)

result = chamfer(result.edges().filter_by(Axis.Z), chamfer_distance)

part = result
part.name = "plate_with_boss_ribs_and_holes"
export_step(part, "output.step")