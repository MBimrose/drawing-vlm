from build123d import *

plate_length = 80.0
plate_width = 50.0
plate_thickness = 8.0
boss_radius = 20.0
boss_height = 30.0
shaft_base_radius = 20.0
shaft_top_radius = 6.0
shaft_length = 30.0
fillet_radius = 1.0
mount_hole_diameter = 6.0
mount_hole_offset = 10.0
keyway_width = 6.0
keyway_depth = 4.0
keyway_length = 20.0

plate = Pos(0, 0, plate_thickness/2) * Box(plate_length, plate_width, plate_thickness)
boss = Pos(0, 0, plate_thickness + boss_height/2) * Cylinder(boss_radius, boss_height)
shaft = Pos(0, 0, plate_thickness + boss_height + shaft_length/2) * Cone(shaft_base_radius, shaft_top_radius, shaft_length)

result = plate + boss + shaft

bottom_edges = result.edges().sort_by(Axis.Z)[:1]
result = fillet(bottom_edges, fillet_radius)

hole_positions = [
    (-plate_length/2 + mount_hole_offset, -plate_width/2 + mount_hole_offset),
    (plate_length/2 - mount_hole_offset, -plate_width/2 + mount_hole_offset),
    (-plate_length/2 + mount_hole_offset, plate_width/2 - mount_hole_offset),
    (plate_length/2 - mount_hole_offset, plate_width/2 - mount_hole_offset),
]
for x, y in hole_positions:
    result = result - Pos(x, y, plate_thickness/2) * Cylinder(mount_hole_diameter/2, plate_thickness)

keyway = Pos(shaft_top_radius + keyway_depth/2, 0, plate_thickness + boss_height + shaft_length/2) * Box(keyway_depth, keyway_width, keyway_length)
result = result - keyway

part = result
part.name = "plate_with_boss_shaft"
export_step(part, "output.step")