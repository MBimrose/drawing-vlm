from build123d import *

channel_width = 60.0
channel_height = 20.0
channel_depth = 30.0
wall_thickness = 2.5
top_radius = 12.0
hole_diameter = 4.0
hole_spacing = 15.0
hole_offset_y = 5.0
fillet_radius = 2.0
chamfer_distance = 0.5

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            l1 = Line((0, 0), (channel_width, 0))
            l2 = Line(l1 @ 1, (channel_width, channel_height - top_radius))
            a1 = ThreePointArc(l2 @ 1, (channel_width/2, channel_height + top_radius), (0, channel_height - top_radius))
            l3 = Line(a1 @ 1, (0, 0))
        make_face()
    extrude(amount=channel_depth)

solid_body = p.part
solid_body = fillet(solid_body.edges().filter_by(Axis.Z), fillet_radius)
top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[top_face])

for i in range(3):
    x = channel_width/2 + (i - 1) * hole_spacing
    y = hole_offset_y
    solid_body = solid_body - Pos(x, y, 0) * Cylinder(hole_diameter/2, channel_depth + 10)

bottom_face = solid_body.faces().sort_by(Axis.Z)[0]
solid_body = chamfer(bottom_face.edges(), chamfer_distance)

part = solid_body
part.name = "channel"
export_step(part, "output.step")