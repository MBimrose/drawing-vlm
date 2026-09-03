from build123d import *

chute_length = 80.0
chute_width = 40.0
chute_height = 30.0
wall_thickness = 3.0
channel_depth = 20.0
channel_top_width = 10.0
channel_bottom_width = 20.0
chamfer_size = 2.0
hole_diameter = 5.0
hole_offset = 10.0
slot_width = 4.0
slot_height = 10.0
slot_spacing = 12.0
slot_count = 3

base = Pos(0, 0, chute_height/2) * Box(chute_length, chute_width, chute_height)

with BuildPart() as p:
    with BuildSketch(Plane.YZ) as sk:
        with BuildLine() as bl:
            Line((-channel_bottom_width/2, 0), (channel_bottom_width/2, 0))
            Line((channel_bottom_width/2, 0), (channel_top_width/2, channel_depth))
            Line((channel_top_width/2, channel_depth), (-channel_top_width/2, channel_depth))
            Line((-channel_top_width/2, channel_depth), (-channel_bottom_width/2, 0))
        make_face()
    extrude(amount=chute_length)
channel = p.part

solid_body = base - channel

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = chamfer(top_face.edges(), chamfer_size)

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[top_face])

hole = Pos(-chute_length/2, -chute_width/2 + hole_offset, chute_height/2) * Rot(0, 90, 0) * Cylinder(hole_diameter/2, chute_length)
solid_body = solid_body - hole

for i in range(slot_count):
    x_pos = i * slot_spacing
    slot = Pos(x_pos, 0, chute_height/2) * Box(slot_width, chute_width, slot_height)
    solid_body = solid_body - slot

part = solid_body
part.name = "chute"
export_step(part, "output.step")