from build123d import *

channel_length = 100.0
channel_width = 60.0
channel_height = 16.0
wall_thickness = 2.0
base_thickness = 4.0
rib_width = 8.0
rib_height = 12.0
rib_thickness = 2.0
hole_diameter = 6.0
hole_spacing = 12.0
hole_offset_from_bottom = 6.0
pocket_width = 30.0
pocket_height = 20.0
pocket_depth = 2.0
chamfer_size = 0.5

solid_body = Pos(0, 0, channel_height/2) * Box(channel_length, channel_width, channel_height)
top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[top_face])
base_plate = Pos(0, 0, base_thickness/2) * Box(channel_length - 2*wall_thickness, channel_width - 2*wall_thickness, base_thickness)
solid_body = solid_body + base_plate
rib = Pos(-channel_length/2 + wall_thickness + rib_width/2, 0, rib_height/2) * Box(rib_width, channel_width - 2*wall_thickness, rib_height)
solid_body = solid_body + rib
for i in range(5):
    y_pos = -channel_width/2 + hole_offset_from_bottom + i * hole_spacing
    hole = Pos(-channel_length/2 + wall_thickness + rib_width/2, y_pos, channel_height/2) * Cylinder(hole_diameter/2, channel_height)
    solid_body = solid_body - hole
pocket = Pos(0, channel_width/2 - pocket_depth/2, channel_height/2) * Box(pocket_width, pocket_depth, pocket_height)
solid_body = solid_body - pocket
top_edges = solid_body.edges().filter_by(Axis.Z).sort_by(Axis.Z)[-1:]
solid_body = chamfer(top_edges, chamfer_size)
part = solid_body
part.name = "channel_with_rib"
export_step(part, "output.step")