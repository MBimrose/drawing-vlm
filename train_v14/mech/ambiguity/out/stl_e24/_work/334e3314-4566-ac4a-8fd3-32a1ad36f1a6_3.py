from build123d import *

plate_width = 80.0
plate_height = 50.0
plate_thickness = 4.0
tab_width = 12.0
tab_height = 20.0
boss_diameter = 20.0
boss_height = 6.0
hole_diameter = 5.2
hole_spacing = 12.0
hole_count = 5
chamfer_distance = 0.5

base_plate = Pos(0, 0, plate_thickness/2) * Box(plate_width, plate_height, plate_thickness)
tab = Pos(plate_width/2 + tab_width/2, 0, plate_thickness/2) * Box(tab_width, tab_height, plate_thickness)
plate_with_tab = base_plate + tab

boss = Pos(0, 0, plate_thickness + boss_height/2) * Cylinder(boss_diameter/2, boss_height)
combined = plate_with_tab + boss

hole_positions = [((i - (hole_count-1)/2) * hole_spacing, 0) for i in range(hole_count)]
hole_depth = plate_thickness + boss_height + 10
for x, y in hole_positions:
    combined = combined - Pos(x, y, plate_thickness + boss_height/2) * Cylinder(hole_diameter/2, hole_depth)

combined = chamfer(combined.edges().filter_by(Axis.Z), chamfer_distance)

part = combined
part.name = "plate_with_tab_boss_and_holes"
export_step(part, "output.step")