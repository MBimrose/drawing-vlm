from build123d import *

channel_width = 60.0
channel_height = 30.0
wall_thickness = 2.5
extrude_depth = 30.0
fillet_radius = 2.0
chamfer_distance = 0.5
hole_diameter = 4.0
hole_spacing = 15.0
hole_offset_y = 5.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            l1 = Line((0, 0), (channel_width, 0))
            l2 = Line(l1 @ 1, (channel_width, channel_height * 0.6))
            arc = ThreePointArc(l2 @ 1, (channel_width / 2, channel_height), (0, channel_height * 0.6))
            l3 = Line(arc @ 1, (0, 0))
        make_face()
    extrude(amount=extrude_depth)

solid_body = p.part

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[top_face])

z_edges = solid_body.edges().filter_by(Axis.Z)
sorted_z = z_edges.sort_by(Axis.X)
fillet_edges = sorted_z[:2] + sorted_z[-2:]
solid_body = fillet(fillet_edges, fillet_radius)

bottom_face = solid_body.faces().sort_by(Axis.Z)[0]
bottom_edges = bottom_face.edges()
solid_body = chamfer(bottom_edges, chamfer_distance)

hole_positions = [
    (hole_spacing, hole_offset_y),
    (channel_width / 2, hole_offset_y),
    (channel_width - hole_spacing, hole_offset_y),
]
for x, y in hole_positions:
    solid_body = solid_body - Pos(x, y, 0) * Cylinder(hole_diameter / 2, channel_height + 10)

part = solid_body
part.name = "channel"
export_step(part, "output.step")