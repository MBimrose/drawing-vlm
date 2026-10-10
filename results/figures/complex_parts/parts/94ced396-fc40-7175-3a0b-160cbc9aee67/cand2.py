from build123d import *

plate_width = 80.0
plate_length = 100.0
plate_thickness = 5.0
slot_width = 20.0
slot_height = 60.0
boss_radius = 12.0
boss_height = 12.0
boss_hole_diameter = 8.0
boss_counterbore_diameter = 14.0
boss_counterbore_depth = 2.5
mount_hole_diameter = 6.0
mount_hole_spacing = 40.0
rib_thickness = 3.0
rib_height = 4.0
chamfer_size = 0.5

result = Box(plate_width, plate_length, plate_thickness)
result = result - Box(slot_width, slot_height, plate_thickness)
result = result + Pos(0, plate_length/2, plate_thickness/2 + boss_height/2) * Cylinder(boss_radius, boss_height)
result = result - Pos(0, plate_length/2, plate_thickness/2 + boss_height/2) * Cylinder(boss_hole_diameter/2, boss_height)
result = result - Pos(0, plate_length/2, plate_thickness/2 + boss_height - boss_counterbore_depth/2) * Cylinder(boss_counterbore_diameter/2, boss_counterbore_depth)
for x in [-mount_hole_spacing/2, mount_hole_spacing/2]:
    result = result - Pos(x, 0, 0) * Cylinder(mount_hole_diameter/2, plate_thickness)
result = result + Pos(-plate_width/2 - rib_thickness/2, 0, 0) * Box(rib_thickness, plate_length, rib_height)
result = chamfer(result.edges().filter_by(Axis.Z), chamfer_size)

part = result
part.name = "plate_with_boss_and_rib"
export_step(part, "output.step")