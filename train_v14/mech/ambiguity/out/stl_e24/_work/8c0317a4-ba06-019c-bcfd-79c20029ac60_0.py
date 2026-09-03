from build123d import *

channel_length = 80.0
channel_width = 40.0
channel_height = 30.0
wall_thickness = 2.5
pocket_length = 40.0
pocket_width = 20.0
pocket_depth = 10.0
hole_diameter = 4.0
hole_depth = 8.0
fillet_radius = 1.2
rib_width = 6.0
rib_height = 4.0
rib_spacing = 15.0
rib_count = int((channel_length - 2 * wall_thickness) // rib_spacing)

solid_body = Pos(0, 0, channel_height / 2) * Box(channel_length, channel_width, channel_height)

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
bottom_face = solid_body.faces().sort_by(Axis.Z)[0]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[top_face, bottom_face])

vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = fillet(vertical_edges, fillet_radius)

pocket = Pos(0, 0, channel_height - pocket_depth / 2) * Box(pocket_length, pocket_width, pocket_depth)
solid_body = solid_body - pocket

hole = Pos(0, 0, channel_height - pocket_depth - hole_depth / 2) * Cylinder(hole_diameter / 2, hole_depth)
solid_body = solid_body - hole

for i in range(rib_count):
    x = (i - (rib_count - 1) / 2) * rib_spacing
    rib = Pos(x, 0, wall_thickness / 2) * Box(rib_width, rib_height, wall_thickness)
    solid_body = solid_body + rib

part = solid_body
part.name = "channel_with_pocket_and_ribs"
export_step(part, "output.step")