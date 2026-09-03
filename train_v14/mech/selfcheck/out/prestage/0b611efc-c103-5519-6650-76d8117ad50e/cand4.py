from build123d import *

leg_width = 12.0
vertical_leg_length = 80.0
horizontal_leg_length = 60.0
bracket_thickness = 8.0
slot_width = 6.0
slot_length = 30.0
slot_depth = bracket_thickness - 1.0
mount_hole_diameter = 4.0
mount_hole_spacing = 30.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0,0), (leg_width,0), (leg_width, vertical_leg_length-leg_width),
                     (horizontal_leg_length, vertical_leg_length-leg_width),
                     (horizontal_leg_length, vertical_leg_length),
                     (0, vertical_leg_length), close=True)
        make_face()
    extrude(amount=bracket_thickness)

solid_body = p.part

slot_center_x = leg_width + (horizontal_leg_length - leg_width) / 2
slot_center_y = vertical_leg_length - leg_width / 2
slot_box = Pos(slot_center_x, slot_center_y, bracket_thickness - slot_depth/2) * Box(slot_width, slot_length, slot_depth)
solid_body = solid_body - slot_box

hole_y1 = vertical_leg_length / 2 - mount_hole_spacing / 2
hole_y2 = vertical_leg_length / 2 + mount_hole_spacing / 2
hole_cyl = Rot(0, 90, 0) * Cylinder(mount_hole_diameter/2, bracket_thickness + 2)
solid_body = solid_body - Pos(leg_width/2, hole_y1, bracket_thickness/2) * hole_cyl
solid_body = solid_body - Pos(leg_width/2, hole_y2, bracket_thickness/2) * hole_cyl

part = solid_body
part.name = "L_Bracket"
export_step(part, "output.step")