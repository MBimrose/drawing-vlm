from build123d import *

leg_length = 80.0
leg_height = 70.0
leg_width = 30.0
thickness = 8.0
inner_fillet_radius = 4.0
hole_diameter = 6.0
hole_spacing = 30.0
hole_offset = 10.0
slot_width = 15.0
slot_height = 8.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            l1 = Line((0, 0), (leg_length, 0))
            l2 = Line(l1@1, (leg_length, leg_width))
            l3 = Line(l2@1, (leg_width + inner_fillet_radius, leg_width))
            arc = RadiusArc(l3@1, (leg_width, leg_width + inner_fillet_radius), inner_fillet_radius)
            l4 = Line(arc@1, (leg_width, leg_height))
            l5 = Line(l4@1, (0, leg_height))
            l6 = Line(l5@1, (0, 0))
        make_face()
    extrude(amount=thickness)

solid = p.part
slot = Pos(leg_width/2, leg_height/2, thickness/2) * Box(slot_width, slot_height, thickness)
solid = solid - slot

hole_positions = [
    (hole_offset, leg_width/2),
    (hole_offset + hole_spacing, leg_width/2),
    (leg_length - hole_offset, leg_width/2),
    (leg_width/2, hole_offset),
    (leg_width/2, hole_offset + hole_spacing),
    (leg_width/2, leg_height - hole_offset),
]
for x, y in hole_positions:
    solid = solid - Pos(x, y, thickness/2) * Cylinder(hole_diameter/2, thickness)

part = solid
part.name = "L_Bracket"
export_step(part, "output.step")