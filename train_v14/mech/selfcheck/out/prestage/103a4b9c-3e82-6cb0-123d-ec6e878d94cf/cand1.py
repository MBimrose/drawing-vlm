from build123d import *

block_length = 70.0
block_width = 30.0
block_height = 20.0
tab_thickness = 5.0
tab_height = 12.0
tab_width = 10.0
flex_slot_width = 3.0
flex_slot_height = 8.0
flex_slot_depth = 2.5
pocket_length = 40.0
pocket_width = 15.0
pocket_depth = 6.0
through_hole_diameter = 4.0
mount_hole_diameter = 3.0
mount_hole_offset = 15.0
chamfer_size = 0.8
fillet_radius = 0.5

base = Pos(0, 0, block_height/2) * Box(block_length, block_width, block_height)
base = chamfer(base.edges().filter_by(Axis.Z), chamfer_size)
base = fillet(base.edges().filter_by(Axis.Z), fillet_radius)

tab = Pos(block_length/2 + tab_thickness/2, 0, block_height/2 + (block_height - tab_height)/2) * Box(tab_thickness, tab_width, tab_height)
result = base + tab

flex_slot = Pos(block_length/2 + tab_thickness - flex_slot_depth/2, 0, block_height/2 + (block_height - tab_height)/2 + tab_height/2) * Box(flex_slot_depth, flex_slot_width, flex_slot_height)
result = result - flex_slot

pocket = Pos(0, 0, pocket_depth/2) * Box(pocket_length, pocket_width, pocket_depth)
result = result - pocket

through_hole = Pos(0, 0, block_height/2) * Cylinder(through_hole_diameter/2, block_height)
result = result - through_hole

mount_hole1 = Pos(0, mount_hole_offset, block_height/2) * Cylinder(mount_hole_diameter/2, block_height)
mount_hole2 = Pos(0, -mount_hole_offset, block_height/2) * Cylinder(mount_hole_diameter/2, block_height)
result = result - mount_hole1 - mount_hole2

part = result
part.name = "snap_fit_block"
export_step(part, "output.step")