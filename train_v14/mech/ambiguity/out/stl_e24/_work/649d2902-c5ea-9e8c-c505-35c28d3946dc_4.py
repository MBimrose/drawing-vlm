from build123d import *

plate_length = 80.0
plate_width = 50.0
plate_thickness = 8.0
boss_diameter = 30.0
boss_height = 12.0
pocket_length = 30.0
pocket_width = 20.0
pocket_depth = 4.0
hole_diameter = 5.0
hole_spacing = 15.0
hole_count = 5
chamfer_distance = 1.0

base = Box(plate_length, plate_width, plate_thickness)
boss = Pos(0, 0, plate_thickness/2) * Cylinder(boss_diameter/2, boss_height)
pocket = Pos(0, 0, plate_thickness/2 + boss_height - pocket_depth/2) * Box(pocket_length, pocket_width, pocket_depth)

solid_body = base + boss - pocket

for i in range(hole_count):
    x = (i - (hole_count - 1) / 2) * hole_spacing
    solid_body = solid_body - Pos(x, 0, 0) * Cylinder(hole_diameter/2, 100)

solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_distance)

part = solid_body
part.name = "plate_with_boss_pocket_and_holes"
export_step(part, "output.step")