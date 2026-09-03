from build123d import *

rod_length = 80.0
rod_diameter = 30.0
rod_radius = rod_diameter / 2.0
groove_width = 15.0
groove_depth = 3.0
groove_length = 30.0
groove_offset = 20.0
hole_diameter = 2.5
hole_spacing = 20.0
hole_offset = 10.0
chamfer_distance = 0.5
tab_width = 12.0
tab_thickness = 3.0
tab_height = 10.0
tab_offset = 5.0

solid_body = Cylinder(rod_radius, rod_length)

groove_box = Pos(rod_radius - groove_depth/2, 0, groove_offset) * Box(groove_depth, groove_width, groove_length)
solid_body = solid_body - groove_box

for i in range(3):
    z_pos = hole_offset + i * hole_spacing
    hole = Pos(rod_radius, 0, z_pos) * Rot(0, 90, 0) * Cylinder(hole_diameter/2, rod_diameter)
    solid_body = solid_body - hole

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
bottom_face = solid_body.faces().sort_by(Axis.Z)[0]
chamfer_edges = top_face.edges() + bottom_face.edges()
solid_body = chamfer(chamfer_edges, chamfer_distance)

tab = Pos(rod_radius - tab_thickness/2, 0, rod_length/2 + tab_offset/2) * Box(tab_width, tab_thickness, tab_height)
solid_body = solid_body + tab

part = solid_body
part.name = "rod_with_groove_holes_and_tab"
export_step(part, "output.step")