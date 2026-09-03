from build123d import *

leg_length = 80.0
leg_height = 70.0
leg_width = 30.0
thickness = 8.0
fillet_radius = 4.0
hole_diameter = 6.0
hole_spacing = 30.0
hole_offset = 10.0
slot_width = 8.0
slot_length = 15.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0, 0), (leg_length, 0), (leg_length, leg_width), (leg_width, leg_width), (leg_width, leg_height), (0, leg_height), close=True)
        make_face()
    extrude(amount=thickness)

solid_body = p.part

inner_edges = [e for e in solid_body.edges().filter_by(Axis.Z) if abs(e.center().X - leg_width) < 1e-3 and abs(e.center().Y - leg_width) < 1e-3]
solid_body = fillet(inner_edges, fillet_radius)

slot = Pos(leg_width/2, leg_height/2, thickness/2) * Box(slot_length, slot_width, thickness)
solid_body = solid_body - slot

hole_r = hole_diameter / 2
hole_cyl = Cylinder(hole_r, thickness)

for x, y in [(hole_offset, leg_width/2), (leg_length - hole_offset, leg_width/2), (leg_width/2, hole_offset), (leg_width/2, leg_height - hole_offset)]:
    solid_body = solid_body - Pos(x, y, thickness/2) * hole_cyl

for x, y in [(hole_offset + hole_spacing, leg_width/2), (leg_width/2, hole_offset + hole_spacing)]:
    solid_body = solid_body - Pos(x, y, thickness/2) * hole_cyl

for x, y in [(leg_width/2, leg_width/2), (leg_width/2, leg_width/2)]:
    solid_body = solid_body - Pos(x, y, thickness/2) * hole_cyl

part = solid_body
part.name = "L_bracket"
export_step(part, "output.step")