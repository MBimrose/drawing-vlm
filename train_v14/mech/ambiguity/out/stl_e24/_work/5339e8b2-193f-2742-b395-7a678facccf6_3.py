from build123d import *

leg_length = 80.0
leg_width = 20.0
thickness = 8.0
rib_thickness = 2.0
rib_height = 20.0
hole_diameter = 6.0
chamfer_size = 1.0
slot_width = 5.0
slot_depth = 6.0
slot_spacing = 15.0
slot_count = 3

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0, 0), (leg_length, 0), (leg_length, leg_width),
                     (leg_width, leg_width), (leg_width, leg_width + leg_width),
                     (0, leg_width + leg_width), close=True)
        make_face()
    extrude(amount=thickness)

solid_body = p.part

vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = chamfer(vertical_edges, chamfer_size)

rib = Pos(leg_width/2, leg_width/2, thickness/2) * Box(rib_thickness, rib_height, thickness)
solid_body = solid_body + rib

hole = Pos(leg_length/2, leg_width/2, thickness/2) * Cylinder(hole_diameter/2, thickness)
solid_body = solid_body - hole

for i in range(slot_count):
    x = leg_width + slot_spacing/2 + i * slot_spacing
    slot = Pos(x, leg_width/2, thickness - thickness/4) * Box(slot_width, slot_depth, thickness/2)
    solid_body = solid_body - slot

part = solid_body
part.name = "L_bracket_with_rib_and_slots"
export_step(part, "output.step")