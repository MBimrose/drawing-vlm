from build123d import *
import math

block_length = 60.0
block_width = 40.0
block_height = 20.0
wall_thickness = 5.0
fillet_radius = 3.0
countersink_diameter = 6.0
countersink_angle = 45.0
hole_diameter = 4.0
hole_spacing = 10.0
hole_offset_from_bottom = 5.0
mount_hole_diameter = 5.0
mount_hole_spacing_x = 20.0
mount_hole_spacing_y = 15.0
rib_height = 2.0
rib_width = 8.0

with BuildPart() as p:
    Box(block_length, block_width, block_height)
solid = p.part
solid = fillet(solid.edges(), fillet_radius)

pocket = Pos(0, 0, block_height/2 - (block_height - wall_thickness)/2) * Box(block_length - 2*wall_thickness, block_width - 2*wall_thickness, block_height - wall_thickness)
solid = solid - pocket

csk_depth = (countersink_diameter/2 - hole_diameter/2) / math.tan(math.radians(countersink_angle/2))
for i in range(3):
    z_pos = -block_height/2 + hole_offset_from_bottom + i*hole_spacing
    csk = Pos(-block_length/2 + csk_depth/2, 0, z_pos) * Rot(0, -90, 0) * Cone(countersink_diameter/2, hole_diameter/2, csk_depth)
    shaft = Pos(0, 0, z_pos) * Rot(0, -90, 0) * Cylinder(hole_diameter/2, block_length + 10)
    solid = solid - csk - shaft

for x, y in [(-mount_hole_spacing_x/2, -mount_hole_spacing_y/2), (mount_hole_spacing_x/2, -mount_hole_spacing_y/2), (-mount_hole_spacing_x/2, mount_hole_spacing_y/2), (mount_hole_spacing_x/2, mount_hole_spacing_y/2)]:
    solid = solid - Pos(x, y, 0) * Cylinder(mount_hole_diameter/2, block_height + 10)

rib = Pos(0, 0, block_height/2 + rib_height/2) * Box(rib_width, block_length - 2*wall_thickness, rib_height)
solid = solid + rib

part = solid
part.name = "block_with_pockets_and_holes"
export_step(part, "output.step")