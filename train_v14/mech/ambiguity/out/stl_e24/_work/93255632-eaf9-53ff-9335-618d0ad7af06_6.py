from build123d import *

outer_width = 80.0
outer_height = 60.0
outer_thickness = 12.0
wall_thickness = 5.0
slot_width = 6.0
slot_length = 30.0
slot_depth = 8.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            l1 = Line((-outer_width/2, 0), (outer_width/2, 0))
            l2 = Line(l1@1, (outer_width/2, outer_height*0.6))
            arc = ThreePointArc(l2@1, (0, outer_height*1.2), (-outer_width/2, outer_height*0.6))
            l3 = Line(arc@1, (-outer_width/2, 0))
        make_face()
    extrude(amount=outer_thickness)

solid_body = p.part
top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[top_face])

slot_box = Pos(0, outer_height/2, 0) * Box(slot_width, slot_length, slot_depth)
solid_body = solid_body - slot_box

part = solid_body
part.name = "shelled_block_with_slot"
export_step(part, "output.step")