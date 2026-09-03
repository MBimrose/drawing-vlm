from build123d import *

outer_width = 80.0
outer_height = 50.0
thickness = 20.0
wall_thickness = 3.0
corner_fillet_radius = 5.0
mount_hole_diameter = 5.0
mount_hole_offset = 8.0
slot_width = 6.0
slot_height = 30.0
slot_offset_y = 0.0

solid_body = Box(outer_width, outer_height, thickness)
solid_body = fillet(solid_body.edges().filter_by(Axis.Z), corner_fillet_radius)
solid_body = solid_body - Box(outer_width - 2*wall_thickness, outer_height - 2*wall_thickness, thickness)

hole_positions = [
    (-outer_width/2 + mount_hole_offset, -outer_height/2 + mount_hole_offset),
    ( outer_width/2 - mount_hole_offset, -outer_height/2 + mount_hole_offset),
    (-outer_width/2 + mount_hole_offset,  outer_height/2 - mount_hole_offset),
    ( outer_width/2 - mount_hole_offset,  outer_height/2 - mount_hole_offset)
]
for x, y in hole_positions:
    solid_body = solid_body - Pos(x, y, 0) * Cylinder(mount_hole_diameter/2, thickness)

slot_depth = wall_thickness + 0.5
solid_body = solid_body - Pos(-outer_width/2 + slot_depth/2, slot_offset_y, 0) * Box(slot_depth, slot_width, slot_height)
solid_body = solid_body - Pos(outer_width/2 - slot_depth/2, slot_offset_y, 0) * Box(slot_depth, slot_width, slot_height)

part = solid_body
part.name = "hollow_frame_with_slots"
export_step(part, "output.step")