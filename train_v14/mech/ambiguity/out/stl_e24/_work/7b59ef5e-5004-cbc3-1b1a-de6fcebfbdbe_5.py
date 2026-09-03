from build123d import *

leg_length = 70.0
leg_height = 55.0
leg_thickness = 12.0
bracket_thickness = 8.0
inner_fillet_radius = 3.0
hole_diameter = 8.0
hole_offset_from_base = 30.0
slot_width = 10.0
slot_length = 20.0
slot_offset_from_end = 5.0
rib_width = 15.0
rib_height = 10.0
rib_thickness = 4.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0, 0), (leg_length, 0), (leg_length, leg_thickness),
                     (leg_thickness, leg_thickness), (leg_thickness, leg_height),
                     (0, leg_height), close=True)
        make_face()
    extrude(amount=bracket_thickness)

solid_body = p.part

inner_edges = [e for e in solid_body.edges().filter_by(Axis.Z)
               if abs(e.center().X - leg_thickness) < 0.1 and abs(e.center().Y - leg_thickness) < 0.1]
solid_body = fillet(inner_edges, inner_fillet_radius)

solid_body = solid_body - Pos(leg_thickness/2, hole_offset_from_base, bracket_thickness/2) * Cylinder(hole_diameter/2, bracket_thickness * 2)

slot_center_x = leg_length - slot_offset_from_end - slot_length/2
solid_body = solid_body - Pos(slot_center_x, leg_thickness/2, bracket_thickness/2) * Box(slot_length, slot_width, bracket_thickness * 2)

rib = Pos(leg_thickness/2, leg_thickness/2, -rib_thickness/2) * Box(rib_width, rib_height, rib_thickness)
solid_body = solid_body + rib

part = solid_body
part.name = "L_bracket"
export_step(part, "output.step")