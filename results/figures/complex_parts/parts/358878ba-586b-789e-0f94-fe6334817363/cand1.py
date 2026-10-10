from build123d import *

channel_length = 80.0
channel_width = 30.0
channel_height = 40.0
wall_thickness = 2.0
slot_width = 20.0
slot_height = 10.0
hole_diameter = 4.0
hole_spacing_x = 20.0
hole_spacing_y = 15.0
hole_rows = 2
hole_cols = 3
chamfer_distance = 0.5

solid_body = Pos(0, 0, channel_height/2) * Box(channel_length, channel_width, channel_height)

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[top_face])

slot_cut = Pos(0, 0, channel_height - slot_height/2) * Box(slot_width, channel_width, slot_height)
solid_body = solid_body - slot_cut

for i in range(hole_cols):
    for j in range(hole_rows):
        x = (i - (hole_cols-1)/2) * hole_spacing_x
        y = (j - (hole_rows-1)/2) * hole_spacing_y
        hole = Pos(x, y, channel_height/2) * Cylinder(hole_diameter/2, channel_height)
        solid_body = solid_body - hole

right_face = solid_body.faces().sort_by(Axis.X)[-1]
right_edges = right_face.edges().filter_by(Axis.Y)
solid_body = chamfer(right_edges, chamfer_distance)

part = solid_body
part.name = "channel_with_slot_and_holes"
export_step(part, "output.step")