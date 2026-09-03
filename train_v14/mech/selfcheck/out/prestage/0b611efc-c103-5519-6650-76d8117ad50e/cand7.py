from build123d import *

vertical_leg_length = 80.0
horizontal_leg_length = 60.0
leg_thickness = 12.0
bracket_thickness = 8.0
slot_width = 6.0
slot_length = 30.0
slot_depth = bracket_thickness - 1.0
mount_hole_diameter = 5.0
mount_hole_offset = 20.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0, 0), (leg_thickness, 0), (leg_thickness, vertical_leg_length - leg_thickness),
                     (horizontal_leg_length, vertical_leg_length - leg_thickness),
                     (horizontal_leg_length, vertical_leg_length), (0, vertical_leg_length), close=True)
        make_face()
    extrude(amount=bracket_thickness)

solid_body = p.part

slot_center_x = leg_thickness + (horizontal_leg_length - leg_thickness) / 2
slot_center_y = vertical_leg_length - leg_thickness / 2
slot_box = Pos(slot_center_x, slot_center_y, bracket_thickness - slot_depth / 2) * Box(slot_width, slot_length, slot_depth)
solid_body = solid_body - slot_box

hole_center_x = leg_thickness / 2
hole_center_y = mount_hole_offset
hole_cyl = Pos(hole_center_x, hole_center_y, bracket_thickness / 2) * Cylinder(mount_hole_diameter / 2, bracket_thickness)
solid_body = solid_body - hole_cyl

part = solid_body
part.name = "L_Bracket"
export_step(part, "output.step")