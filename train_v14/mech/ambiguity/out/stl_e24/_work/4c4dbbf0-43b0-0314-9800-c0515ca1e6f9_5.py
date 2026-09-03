from build123d import *

outer_width = 60.0
outer_height = 40.0
channel_length = 80.0
wall_thickness = 4.0
inner_width = outer_width - 2 * wall_thickness
inner_height = outer_height - 2 * wall_thickness
chamfer_size = 2.0
hole_diameter = 4.0
hole_spacing = 20.0
hole_offset_from_start = 10.0

outer = Box(outer_width, outer_height, channel_length)
inner = Box(inner_width, inner_height, channel_length - 2 * wall_thickness)
solid_body = outer - inner

bottom_face = solid_body.faces().sort_by(Axis.Z)[0]
bottom_edges = bottom_face.edges()
solid_body = chamfer(bottom_edges, chamfer_size)

for i in range(3):
    y_pos = (i - 1) * hole_spacing
    hole = Pos(outer_width / 2, y_pos, -channel_length / 2 + hole_offset_from_start) * Rot(0, 90, 0) * Cylinder(hole_diameter / 2, outer_width + 10)
    solid_body = solid_body - hole

part = solid_body
part.name = "channel_with_holes"
export_step(part, "output.step")