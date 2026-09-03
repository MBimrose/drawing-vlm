from build123d import *

rail_length = 100.0
rail_width = 30.0
rail_height = 20.0
wall_thickness = 3.0
keyway_width = 10.0
keyway_depth = 8.0
fillet_radius = 2.0
mount_hole_dia = 5.0
mount_hole_spacing = 40.0
mount_hole_offset = 10.0

solid = Box(rail_length, rail_width, rail_height)
solid = fillet(solid.edges(), fillet_radius)

inner = Box(rail_length - 2*wall_thickness, rail_width - 2*wall_thickness, rail_height)
solid = solid - inner

keyway = Box(rail_length - 20, keyway_width, keyway_depth)
keyway = Pos(0, -rail_width/2 + wall_thickness + keyway_width/2, -rail_height/2 + keyway_depth/2) * keyway
solid = solid - keyway

hole_positions = [
    (rail_length/2 - mount_hole_offset, -rail_width/2 + mount_hole_offset),
    (rail_length/2 - mount_hole_offset - mount_hole_spacing, -rail_width/2 + mount_hole_offset)
]
for x, y in hole_positions:
    solid = solid - Pos(x, y, 0) * Cylinder(mount_hole_dia/2, rail_height)

part = solid
part.name = "rail_with_keyway_and_mount_holes"
export_step(part, "output.step")