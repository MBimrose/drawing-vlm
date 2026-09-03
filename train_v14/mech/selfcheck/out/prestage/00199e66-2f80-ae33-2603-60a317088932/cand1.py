from build123d import *
import math

block_length = 80.0
block_width = 60.0
block_thickness = 12.0
pocket_length = 60.0
pocket_width = 40.0
pocket_depth = 4.0
blind_hole_diameter = 30.0
blind_hole_depth = 6.0
mount_hole_diameter = 5.0
mount_hole_offset = 15.0
countersink_diameter = 10.0
countersink_angle = 82.0
rib_thickness = 4.0
rib_height = 6.0
rib_offset = 10.0
chamfer_size = 1.0

solid_body = Box(block_length, block_width, block_thickness)
solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_size)

pocket = Pos(0, 0, block_thickness - pocket_depth/2) * Box(pocket_length, pocket_width, pocket_depth)
solid_body = solid_body - pocket

blind_hole = Pos(0, 0, block_thickness/2 - blind_hole_depth/2) * Cylinder(blind_hole_diameter/2, blind_hole_depth)
solid_body = solid_body - blind_hole

csk_half_angle = math.radians(countersink_angle / 2)
csk_height = (countersink_diameter/2 - mount_hole_diameter/2) / math.tan(csk_half_angle)

for x, y in [(-block_length/2 + mount_hole_offset, -block_width/2 + mount_hole_offset),
             (block_length/2 - mount_hole_offset, -block_width/2 + mount_hole_offset),
             (-block_length/2 + mount_hole_offset, block_width/2 - mount_hole_offset),
             (block_length/2 - mount_hole_offset, block_width/2 - mount_hole_offset)]:
    shaft = Pos(x, y, 0) * Cylinder(mount_hole_diameter/2, block_thickness)
    solid_body = solid_body - shaft
    csk = Pos(x, y, block_thickness/2 - csk_height/2) * Cone(mount_hole_diameter/2, countersink_diameter/2, csk_height)
    solid_body = solid_body - csk

rib1 = Pos(-block_length/2 + rib_offset, 0, -block_thickness/2 + rib_height/2) * Box(rib_thickness, block_width - 2*rib_offset, rib_height)
solid_body = solid_body + rib1
rib2 = Pos(block_length/2 - rib_offset, 0, -block_thickness/2 + rib_height/2) * Box(rib_thickness, block_width - 2*rib_offset, rib_height)
solid_body = solid_body + rib2

part = solid_body
part.name = "mounting_block_with_pockets_and_ribs"
export_step(part, "output.step")