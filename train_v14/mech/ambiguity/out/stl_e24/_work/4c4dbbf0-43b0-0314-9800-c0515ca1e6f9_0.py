from build123d import *

outer_width = 60.0
outer_height = 40.0
length = 80.0
wall_thickness = 4.0
pocket_width = 30.0
pocket_height = 20.0
pocket_depth = 6.0
hole_diameter = 4.0
hole_spacing = 20.0
hole_offset = 10.0

solid_body = Box(outer_width, outer_height, length)
inner = Box(outer_width - 2*wall_thickness, outer_height - 2*wall_thickness, length - 2*wall_thickness)
solid_body = solid_body - inner

pocket = Box(pocket_width, pocket_height, pocket_depth)
pocket = Pos(0, 0, length/2 - pocket_depth/2) * pocket
solid_body = solid_body - pocket

num_holes = int((length - 2*hole_offset) // hole_spacing) + 1
for i in range(num_holes):
    z_pos = -length/2 + hole_offset + i*hole_spacing
    hole = Cylinder(hole_diameter/2, outer_width + 10)
    hole = Rot(0, 90, 0) * hole
    hole = Pos(0, 0, z_pos) * hole
    solid_body = solid_body - hole

part = solid_body
part.name = "hollow_box_with_pocket_and_holes"
export_step(part, "output.step")