from build123d import *

plate_width = 80.0
plate_height = 100.0
plate_thickness = 5.0
slot_width = 30.0
slot_height = 60.0
boss_radius = 12.0
boss_height = 12.0
boss_hole_diameter = 8.0
boss_hole_cbore_diameter = 14.0
boss_hole_cbore_depth = 2.5
mount_hole_diameter = 6.0
mount_hole_cbore_diameter = 10.0
mount_hole_cbore_depth = 2.0
mount_hole_spacing = 50.0
mount_hole_offset_y = -20.0
rib_thickness = 3.0
chamfer_size = 0.5

result = Box(plate_width, plate_height, plate_thickness)
result = result - Box(slot_width, slot_height, plate_thickness)

for x, y in [(-mount_hole_spacing/2, mount_hole_offset_y), (mount_hole_spacing/2, mount_hole_offset_y)]:
    result = result - Pos(x, y, 0) * Cylinder(mount_hole_diameter/2, plate_thickness)
    result = result - Pos(x, y, plate_thickness/2 - mount_hole_cbore_depth/2) * Cylinder(mount_hole_cbore_diameter/2, mount_hole_cbore_depth)

result = result + Pos(0, plate_height/2, plate_thickness/2 + boss_height/2) * Cylinder(boss_radius, boss_height)
result = result - Pos(0, plate_height/2, plate_thickness/2 + boss_height/2) * Cylinder(boss_hole_diameter/2, boss_height + plate_thickness)
result = result - Pos(0, plate_height/2, plate_thickness/2 + boss_height - boss_hole_cbore_depth/2) * Cylinder(boss_hole_cbore_diameter/2, boss_hole_cbore_depth)

result = result + Pos(-plate_width/2 - rib_thickness/2, 0, 0) * Box(rib_thickness, plate_height, rib_thickness)

result = chamfer(result.edges().filter_by(Axis.Z), chamfer_size)

part = result
part.name = "plate_with_boss_and_rib"
export_step(part, "output.step")