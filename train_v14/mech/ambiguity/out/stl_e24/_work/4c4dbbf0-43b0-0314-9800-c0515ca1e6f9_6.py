from build123d import *

outer_width = 60.0
outer_height = 40.0
length = 80.0
wall_thickness = 4.0
hole_diameter = 4.0
hole_spacing = 20.0
hole_offset = 10.0
chamfer_size = 1.0

solid_body = Box(outer_width, outer_height, length)
inner = Box(outer_width - 2*wall_thickness, outer_height - 2*wall_thickness, length - 2*wall_thickness)
solid_body = solid_body - inner

num_holes = int((outer_width - 2*wall_thickness) // hole_spacing) + 1
for i in range(num_holes):
    y_pos = (i - (num_holes - 1) / 2) * hole_spacing
    hole = Pos(outer_width/2, y_pos, -length/2 + hole_offset) * Rot(0, 90, 0) * Cylinder(hole_diameter/2, outer_width)
    solid_body = solid_body - hole

part = solid_body
part.name = "hollow_box_with_holes"
export_step(part, "output.step")