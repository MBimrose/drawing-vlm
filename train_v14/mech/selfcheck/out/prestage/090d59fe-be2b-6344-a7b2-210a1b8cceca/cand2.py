from build123d import *

channel_length = 80.0
channel_width = 40.0
channel_height = 30.0
wall_thickness = 3.0
chamfer_size = 1.0
hole_diameter = 5.0
hole_offset_y = -10.0
slot_width = 4.0
slot_height = 10.0
slot_spacing = 12.0
slot_count = 3

with BuildPart() as p:
    with BuildSketch(Plane.YZ) as sk:
        with BuildLine() as bl:
            Line((-channel_width/2, 0), (-channel_width/2, channel_height))
            Line((-channel_width/2, channel_height), (channel_width/2, channel_height/2))
            Line((channel_width/2, channel_height/2), (channel_width/2, 0))
            Line((channel_width/2, 0), (-channel_width/2, 0))
        make_face()
    extrude(amount=channel_length)

solid_body = p.part
top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[top_face])

top_edges = solid_body.faces().sort_by(Axis.Z)[-1].edges()
solid_body = chamfer(top_edges, chamfer_size)

hole_cyl = Rot(0, 90, 0) * Cylinder(hole_diameter/2, channel_length + 20)
solid_body = solid_body - Pos(0, hole_offset_y, channel_height/2) * hole_cyl
solid_body = solid_body - Pos(channel_length, hole_offset_y, channel_height/2) * hole_cyl

for i in range(slot_count):
    x_pos = channel_length/2 + i * slot_spacing
    slot_box = Box(slot_width, wall_thickness, slot_height)
    solid_body = solid_body - Pos(x_pos, channel_width/2 - wall_thickness/2, channel_height/2) * slot_box
    solid_body = solid_body - Pos(x_pos, -channel_width/2 + wall_thickness/2, channel_height/2) * slot_box

part = solid_body
part.name = "channel_with_holes_and_slots"
export_step(part, "output.step")