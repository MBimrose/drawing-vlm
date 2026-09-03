from build123d import *

channel_length = 80.0
channel_width = 20.0
channel_height = 30.0
wall_thickness = 1.0
chamfer_size = 0.5
hole_diameter = 5.5
hole_spacing = 15.0
hole_offset_from_bottom = 6.0

with BuildPart() as p:
    with BuildSketch(Plane.YZ) as sk:
        with BuildLine() as bl:
            l1 = Line((0, 0), (channel_width, 0))
            l2 = Line(l1 @ 1, (channel_width, channel_height))
            l3 = Line(l2 @ 1, (0, channel_height))
            l4 = Line(l3 @ 1, (0, 0))
        make_face()
    extrude(amount=channel_length)

solid_body = p.part
top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[top_face])

z_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = chamfer(z_edges, chamfer_size)

for i in range(4):
    z_pos = hole_offset_from_bottom + i * hole_spacing
    hole = Pos(0, channel_width / 2, z_pos) * Rot(0, 90, 0) * Cylinder(hole_diameter / 2, channel_length)
    solid_body = solid_body - hole

part = solid_body
part.name = "channel"
export_step(part, "output.step")