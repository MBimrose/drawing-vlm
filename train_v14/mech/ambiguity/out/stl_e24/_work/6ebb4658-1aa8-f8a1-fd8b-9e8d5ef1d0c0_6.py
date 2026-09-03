from build123d import *

block_length = 80.0
block_width = 50.0
block_height = 30.0
wall_thickness = 4.0
central_hole_diameter = 12.0
counterbore_diameter = 20.0
counterbore_depth = 10.0
mount_hole_diameter = 5.0
mount_hole_offset = 5.0
rib_thickness = 3.0
rib_height = 8.0
rib_length = 20.0
slot_width = 6.0
slot_length = 25.0
slot_depth = 8.0
chamfer_distance = 1.0

result = Box(block_length, block_width, block_height)

result = result - Cylinder(central_hole_diameter/2, block_height)
result = result - Pos(0, 0, block_height/2 - counterbore_depth/2) * Cylinder(counterbore_diameter/2, counterbore_depth)

mount_x = block_length/2 - wall_thickness/2
mount_z = block_height/2 - mount_hole_offset
result = result - Pos(mount_x, 0, mount_z) * Rot(90, 0, 0) * Cylinder(mount_hole_diameter/2, block_width)
result = result - Pos(-mount_x, 0, mount_z) * Rot(90, 0, 0) * Cylinder(mount_hole_diameter/2, block_width)

rib = Pos(0, 0, block_height/2 - rib_height/2) * Box(rib_length, rib_thickness, rib_height)
result = result + rib

slot = Pos(0, -block_width/2 + slot_depth/2, 0) * Box(slot_length, slot_depth, slot_width)
result = result - slot

bottom_face = result.faces().sort_by(Axis.Z)[0]
result = chamfer(bottom_face.edges(), chamfer_distance)

part = result
part.name = "block_with_holes_rib_and_slot"
export_step(part, "output.step")