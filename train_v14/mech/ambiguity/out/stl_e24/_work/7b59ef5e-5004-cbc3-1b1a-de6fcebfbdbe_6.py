from build123d import *

leg_length_horizontal = 70.0
leg_length_vertical = 55.0
leg_thickness = 12.0
bracket_thickness = 8.0
inner_fillet_radius = 4.0
hole_diameter = 8.0
hole_offset_from_inner = 20.0
slot_length = 20.0
slot_width = 10.0
slot_offset_from_inner = 30.0
rib_height = 4.0
rib_width = 15.0
rib_thickness = 6.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0,0), (leg_length_horizontal, 0), (leg_length_horizontal, leg_thickness),
                     (leg_thickness, leg_thickness), (leg_thickness, leg_length_vertical),
                     (0, leg_length_vertical), close=True)
        make_face()
    extrude(amount=bracket_thickness)

solid_body = p.part

inner_edges = [e for e in solid_body.edges().filter_by(Axis.Z) if abs(e.center().X - leg_thickness) < 0.1 and abs(e.center().Y - leg_thickness) < 0.1]
solid_body = fillet(inner_edges, inner_fillet_radius)

hole_x = leg_thickness / 2
hole_y = leg_length_vertical / 2
solid_body = solid_body - Pos(hole_x, hole_y, bracket_thickness/2) * Cylinder(hole_diameter/2, bracket_thickness + 1)

slot_x = slot_offset_from_inner + slot_length / 2
slot_y = leg_thickness / 2
solid_body = solid_body - Pos(slot_x, slot_y, bracket_thickness/2) * Box(slot_length, slot_width, bracket_thickness + 1)

rib = Pos(rib_thickness/2, rib_width/2, -rib_height/2) * Box(rib_thickness, rib_width, rib_height)
solid_body = solid_body + rib

part = solid_body
part.name = "L_bracket"
export_step(part, "output.step")