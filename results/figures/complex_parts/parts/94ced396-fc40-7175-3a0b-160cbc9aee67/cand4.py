from build123d import *

plate_width = 80.0
plate_length = 100.0
plate_thickness = 5.0
boss_radius = 12.0
boss_height = 12.0
hole_diameter = 6.0
hole_spacing = 40.0
chamfer_size = 1.0
slot_width = 30.0
slot_length = 40.0
slot_offset = 20.0
rib_thickness = 3.0
rib_height = 40.0
counterbore_diameter = 8.0
counterbore_depth = 2.5

base = Box(plate_width, plate_length, plate_thickness)
boss = Pos(0, plate_length/2 + boss_radius/2, plate_thickness/2 + boss_height/2) * Cylinder(boss_radius, boss_height)
result = base + boss

for x, y in [(-hole_spacing/2, 0), (hole_spacing/2, 0)]:
    result = result - Pos(x, y, 0) * Cylinder(hole_diameter/2, plate_thickness + 1)

result = chamfer(result.edges().filter_by(Axis.Z), chamfer_size)

slot_center_x = plate_width/2 - slot_offset
result = result - Pos(slot_center_x, 0, 0) * Box(slot_width, slot_length, plate_thickness + 1)

rib = Pos(-plate_width/2 - rib_thickness/2, 0, 0) * Box(rib_thickness, rib_height, plate_thickness)
result = result + rib

cbore_x = 0
cbore_y = plate_length/2 + boss_radius/2
result = result - Pos(cbore_x, cbore_y, plate_thickness/2 + boss_height - counterbore_depth/2) * Cylinder(counterbore_diameter*1.5/2, counterbore_depth)
result = result - Pos(cbore_x, cbore_y, plate_thickness/2 + boss_height/2) * Cylinder(counterbore_diameter/2, plate_thickness + boss_height + 1)

part = result
part.name = "plate_with_boss_and_features"
export_step(part, "output.step")