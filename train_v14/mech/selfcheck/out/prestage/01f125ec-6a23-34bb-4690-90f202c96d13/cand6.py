from build123d import *

long_leg = 80.0
short_leg = 70.0
leg_width = 30.0
thickness = 8.0
inner_fillet = 4.0
notch_width = 15.0
notch_height = 8.0
notch_offset = 10.0
hole_diameter = 6.0
hole_spacing = 20.0
hole_offset = 10.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0,0), (long_leg,0), (long_leg,leg_width), (leg_width,leg_width), (leg_width,short_leg), (0,short_leg), close=True)
        make_face()
    extrude(amount=thickness)

solid_body = p.part
inner_edge = [e for e in solid_body.edges().filter_by(Axis.Z) if abs(e.center().X - leg_width) < 1e-3 and abs(e.center().Y - leg_width) < 1e-3][0]
solid_body = fillet([inner_edge], inner_fillet)

notch_center_x = leg_width/2 - notch_offset - notch_width/2
notch_center_y = short_leg/2
solid_body = solid_body - Pos(notch_center_x, notch_center_y, thickness/2) * Box(notch_width, notch_height, thickness)

hole_positions = [
    (hole_offset, leg_width/2),
    (hole_offset + hole_spacing, leg_width/2),
    (leg_width/2, hole_offset),
    (leg_width/2, hole_offset + hole_spacing),
]
for x, y in hole_positions:
    solid_body = solid_body - Pos(x, y, thickness/2) * Cylinder(hole_diameter/2, thickness)

part = solid_body
part.name = "L_Bracket"
export_step(part, "output.step")