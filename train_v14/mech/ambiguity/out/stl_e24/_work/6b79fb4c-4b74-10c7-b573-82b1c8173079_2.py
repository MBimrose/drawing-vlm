from build123d import *

channel_width = 80.0
channel_height = 40.0
web_thickness = 5.0
flange_thickness = 5.0
length = 100.0
chamfer_size = 2.0
hole_diameter = 3.0
hole_spacing_x = 12.0
hole_spacing_y = 12.0
hole_rows = 3
hole_cols = 4
pocket_width = 30.0
pocket_height = 20.0
pocket_depth = 3.0
clearance_hole_diameter = 8.0

outer = Box(channel_width, length, channel_height)
inner = Pos(web_thickness/2, 0, 0) * Box(channel_width - web_thickness, length, channel_height - 2*flange_thickness)
result = outer - inner

top_face = result.faces().sort_by(Axis.Z)[-1]
result = chamfer(top_face.edges(), chamfer_size)

pocket = Pos(-channel_width/2 + pocket_depth/2, 0, 0) * Box(pocket_depth, pocket_width, pocket_height)
result = result - pocket

clearance_hole = Pos(-channel_width/2 + web_thickness/2, 0, 0) * Rot(0, 90, 0) * Cylinder(clearance_hole_diameter/2, web_thickness)
result = result - clearance_hole

for i in range(hole_cols):
    for j in range(hole_rows):
        y = (i - (hole_cols-1)/2) * hole_spacing_x
        z = (j - (hole_rows-1)/2) * hole_spacing_y
        hole = Pos(-channel_width/2 + web_thickness/2, y, z) * Rot(0, 90, 0) * Cylinder(hole_diameter/2, web_thickness)
        result = result - hole

part = result
part.name = "C_channel_with_holes"
export_step(part, "output.step")