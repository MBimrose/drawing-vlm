from build123d import *

block_length = 80
block_width = 50
block_height = 30
bearing_diameter = 30
bearing_clearance = 2
bearing_seat_depth = 10
through_hole_diameter = 6
through_hole_offset_x = 20
through_hole_offset_y = 15
fillet_radius = 2
mount_hole_diameter = 4
mount_hole_spacing_x = 30
mount_hole_spacing_y = 20
rib_thickness = 5
rib_height = 10
slot_width = 6
slot_height = 20
slot_depth = 8

solid_body = Box(block_length, block_width, block_height)

bearing_center_x = -block_length/2 + 20
bearing_center_y = -block_width/2 + 15
bearing_radius = (bearing_diameter + bearing_clearance)/2
solid_body = solid_body - Pos(bearing_center_x, bearing_center_y, block_height - bearing_seat_depth/2) * Cylinder(bearing_radius, bearing_seat_depth)

through_hole_x = through_hole_offset_x
through_hole_y = through_hole_offset_y
solid_body = solid_body - Pos(through_hole_x, through_hole_y, 0) * Cylinder(through_hole_diameter/2, block_height)

solid_body = fillet(solid_body.edges().filter_by(Axis.Z), fillet_radius)

mount_points = [
    (-mount_hole_spacing_x/2, -mount_hole_spacing_y/2),
    (mount_hole_spacing_x/2, -mount_hole_spacing_y/2),
    (-mount_hole_spacing_x/2, mount_hole_spacing_y/2),
    (mount_hole_spacing_x/2, mount_hole_spacing_y/2),
]
for x, y in mount_points:
    solid_body = solid_body - Pos(x, y, 0) * Cylinder(mount_hole_diameter/2, block_height)

rib = Pos(block_length/2 - rib_thickness/2, 0, 0) * Box(rib_thickness, rib_height, block_height/2)
solid_body = solid_body + rib

slot = Pos(block_length/2 - slot_depth/2, 0, 0) * Box(slot_depth, slot_width, slot_height)
solid_body = solid_body - slot

part = solid_body
part.name = "bearing_block"
export_step(part, "output.step")