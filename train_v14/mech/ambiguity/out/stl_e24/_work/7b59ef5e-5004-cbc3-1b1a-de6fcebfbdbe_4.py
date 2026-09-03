from build123d import *

leg_length = 70.0
leg_height = 55.0
leg_thickness = 12.0
bracket_thickness = 8.0
inner_fillet_radius = 3.0
hole_diameter = 8.0
slot_width = 10.0
slot_length = 20.0
rib_thickness = 4.0
rib_width = 15.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            l1 = Line((0, 0), (leg_length, 0))
            l2 = Line(l1@1, (leg_length, leg_thickness))
            l3 = Line(l2@1, (leg_thickness, leg_thickness))
            l4 = Line(l3@1, (leg_thickness, leg_height))
            l5 = Line(l4@1, (0, leg_height))
            l6 = Line(l5@1, (0, 0))
        make_face()
    extrude(amount=bracket_thickness)

solid_body = p.part

inner_edges = [e for e in solid_body.edges().filter_by(Axis.Z) if abs(e.center().X - leg_thickness) < 1e-3 and abs(e.center().Y - leg_thickness) < 1e-3]
solid_body = fillet(inner_edges, inner_fillet_radius)

solid_body = solid_body - Pos(leg_thickness/2, leg_height/2, bracket_thickness/2) * Cylinder(hole_diameter/2, bracket_thickness * 2)

solid_body = solid_body - Pos(leg_length/2, leg_thickness/2, bracket_thickness/2) * Box(slot_length, slot_width, bracket_thickness * 2)

rib = Pos(leg_thickness/2, leg_thickness/2, -rib_thickness/2) * Box(rib_width, leg_thickness, rib_thickness)
solid_body = solid_body + rib

part = solid_body
part.name = "L_bracket"
export_step(part, "output.step")