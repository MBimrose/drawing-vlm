from build123d import *

handle_length = 80.0
handle_diameter = 30.0
handle_radius = handle_diameter / 2.0
groove_width = 8.0
groove_depth = 1.5
groove_position = 30.0
tab_width = 12.0
tab_thickness = 3.0
tab_height = 5.0
chamfer_size = 0.5
hole_diameter = 2.5
hole_depth = 4.0
hole_spacing = 20.0
hole_count = 3

solid_body = Cylinder(handle_radius, handle_length)
solid_body = chamfer(solid_body.edges(), chamfer_size)

groove_cut = Pos(handle_radius - groove_depth/2, groove_position, 0) * Box(groove_depth, groove_width, handle_length)
solid_body = solid_body - groove_cut

tab = Pos(handle_radius - tab_thickness/2, 0, handle_length/2 + tab_height/2) * Box(tab_width, tab_thickness, tab_height)
solid_body = solid_body + tab

for i in range(hole_count):
    z_pos = handle_length/2 - (hole_count-1)*hole_spacing/2 + i * hole_spacing
    hole = Pos(handle_radius - hole_depth/2, 0, z_pos) * Rot(0, 90, 0) * Cylinder(hole_diameter/2, hole_depth)
    solid_body = solid_body - hole

part = solid_body
part.name = "handle_with_groove_tab_holes"
export_step(part, "output.step")