from build123d import *

horizontal_leg_length = 70.0
vertical_leg_length = 55.0
leg_width = 12.0
thickness = 8.0
inner_fillet_radius = 2.0
hole_diameter = 8.0
hole_offset_from_base = 30.0
slot_length = 20.0
slot_width = 10.0
slot_offset_from_end = 15.0
rib_length = 15.0
rib_width = 10.0
rib_height = 4.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0, 0), (horizontal_leg_length, 0), (horizontal_leg_length, leg_width),
                     (leg_width, leg_width), (leg_width, vertical_leg_length), (0, vertical_leg_length), close=True)
        make_face()
    extrude(amount=thickness)

solid_body = p.part

inner_edges = [e for e in solid_body.edges().filter_by(Axis.Z) if abs(e.center().X - leg_width) < 0.1 and abs(e.center().Y - leg_width) < 0.1]
solid_body = fillet(inner_edges, inner_fillet_radius)

solid_body = solid_body - Pos(leg_width/2, hole_offset_from_base, thickness/2) * Cylinder(hole_diameter/2, thickness)

slot_center_x = horizontal_leg_length - slot_offset_from_end - slot_length/2
solid_body = solid_body - Pos(slot_center_x, leg_width/2, thickness/2) * Box(slot_length, slot_width, thickness)

rib = Pos(leg_width/2, leg_width/2, -rib_height/2) * Box(rib_length, rib_width, rib_height)
solid_body = solid_body + rib

part = solid_body
part.name = "L_Bracket"
export_step(part, "output.step")