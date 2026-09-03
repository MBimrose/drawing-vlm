from build123d import *

channel_width = 60.0
channel_height = 30.0
wall_thickness = 2.5
fillet_radius = 2.0
chamfer_distance = 0.5
hole_diameter = 4.0
hole_spacing = 15.0
hole_offset_y = 5.0
hole_count = 3

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            l1 = Line((0, 0), (channel_width, 0))
            l2 = Line(l1 @ 1, (channel_width, channel_height * 0.6))
            a1 = ThreePointArc(l2 @ 1, (channel_width * 0.5, channel_height * 1.1), (0, channel_height * 0.6))
            l3 = Line(a1 @ 1, (0, 0))
        make_face()
    extrude(amount=channel_height)

solid_body = p.part
top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[top_face])

z_edges = solid_body.edges().filter_by(Axis.Z)
fillet_edges = [e for e in z_edges if e.center().Y < channel_height * 0.5]
solid_body = fillet(fillet_edges, fillet_radius)

bottom_face = solid_body.faces().sort_by(Axis.Z)[0]
bottom_edges = bottom_face.edges()
solid_body = chamfer(bottom_edges, chamfer_distance)

for i in range(hole_count):
    x = channel_width / 2 + (i - (hole_count - 1) / 2) * hole_spacing
    y = hole_offset_y
    solid_body = solid_body - Pos(x, y, channel_height / 2) * Cylinder(hole_diameter / 2, channel_height + 10)

part = solid_body
part.name = "channel"
export_step(part, "output.step")