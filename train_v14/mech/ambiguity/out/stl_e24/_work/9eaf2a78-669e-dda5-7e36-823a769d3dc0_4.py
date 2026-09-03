from build123d import *

leg_length = 80.0
leg_height = 65.0
leg_thickness = 12.0
bracket_thickness = 8.0
slot_width = 10.0
slot_height = 6.0
hole_diameter = 6.0
hole_depth = 5.0
hole_spacing = 20.0
fillet_radius = 1.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0, 0), (leg_length, 0), (leg_length, leg_thickness),
                     (leg_thickness, leg_thickness), (leg_thickness, leg_height),
                     (0, leg_height), close=True)
        make_face()
    extrude(amount=bracket_thickness)

solid_body = p.part
solid_body = fillet(solid_body.edges().filter_by(Axis.Z), fillet_radius)

slot_box = Box(slot_width, slot_height, bracket_thickness)
solid_body = solid_body - Pos(leg_thickness/2, leg_height/2, bracket_thickness/2) * slot_box

for y_pos in [leg_thickness/2 - hole_spacing/2, leg_thickness/2 + hole_spacing/2]:
    hole = Cylinder(hole_diameter/2, hole_depth)
    solid_body = solid_body - Pos(leg_length - hole_depth/2, y_pos, bracket_thickness/2) * Rot(0, 90, 0) * hole

part = solid_body
part.name = "L_bracket"
export_step(part, "output.step")