from build123d import *

channel_length = 80.0
channel_width = 30.0
channel_height = 20.0
wall_thickness = 1.0
notch_width = 5.0
notch_height = 8.0
hole_diameter = 4.0
hole_spacing = 12.0
hole_count = 3
chamfer_size = 0.5

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            l1 = Line((0, 0), (channel_length, 0))
            l2 = Line(l1 @ 1, (channel_length, channel_width))
            l3 = Line(l2 @ 1, (channel_length - notch_width, channel_width))
            arc = ThreePointArc(l3 @ 1, (channel_length/2, channel_width + 5), (0, channel_width))
            l4 = Line(arc @ 1, (0, 0))
        make_face()
    extrude(amount=channel_height)

solid_body = p.part
bottom_face = solid_body.faces().sort_by(Axis.Z)[0]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[bottom_face])

notch_box = Box(wall_thickness*2, notch_width, notch_height)
notch_box = Pos(channel_length - wall_thickness, channel_width/2, channel_height/2) * notch_box
solid_body = solid_body - notch_box

for i in range(hole_count):
    x = channel_length/2 + (i - (hole_count-1)/2) * hole_spacing
    hole = Cylinder(hole_diameter/2, channel_height + 10)
    hole = Pos(x, channel_width/2, channel_height/2) * hole
    solid_body = solid_body - hole

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
top_edges = top_face.edges()
solid_body = chamfer(top_edges, chamfer_size)

part = solid_body
part.name = "channel_with_notch_and_holes"
export_step(part, "output.step")