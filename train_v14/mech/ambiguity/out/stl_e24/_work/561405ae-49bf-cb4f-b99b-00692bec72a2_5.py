from build123d import *

block_length = 80.0
block_width = 50.0
block_height = 30.0
slot_length = 40.0
slot_width = 10.0
slot_depth = 15.0
countersink_diameter = 12.0
countersink_angle = 90.0
countersink_depth = 5.0
mount_hole_diameter = 6.0
mount_hole_spacing = 30.0
mount_hole_offset = 10.0
rib_height = 5.0
rib_width = 20.0
rib_length = 30.0
fillet_radius = 4.0
chamfer_distance = 2.0

solid_body = Box(block_length, block_width, block_height)
solid_body = solid_body - Pos(-block_length/2 + slot_length/2, -block_width/2 + slot_depth/2, 0) * Box(slot_length, slot_depth, slot_width)
solid_body = solid_body - Pos(0, 0, block_height/2) * CounterSinkHole(countersink_diameter/2, countersink_diameter/2, countersink_depth, countersink_angle)
for x, y in [(-mount_hole_spacing/2, -mount_hole_offset), (mount_hole_spacing/2, -mount_hole_offset), (-mount_hole_spacing/2, mount_hole_offset), (mount_hole_spacing/2, mount_hole_offset)]:
    solid_body = solid_body - Pos(x, y, block_height/2) * CounterSinkHole(mount_hole_diameter/2, mount_hole_diameter/2, countersink_depth, countersink_angle)
solid_body = solid_body + Pos(0, 0, block_height/2 - rib_height/2) * Box(rib_length, rib_width, rib_height)
solid_body = fillet(solid_body.edges().filter_by(Axis.Z).sort_by(Axis.X)[-2:], fillet_radius)
top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = chamfer(top_face.edges(), chamfer_distance)
part = solid_body
part.name = "block_with_slot_and_holes"
export_step(part, "output.step")