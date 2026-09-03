from build123d import *

leg_length_long = 70.0
leg_length_short = 55.0
leg_thickness = 12.0
bracket_thickness = 8.0
inner_fillet_radius = 3.0
hole_diameter = 8.0
hole_offset_from_inner = 20.0
slot_width = 10.0
slot_length = 20.0
rib_width = 15.0
rib_length = 10.0
rib_thickness = 4.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0, 0), (leg_length_long, 0), (leg_length_long, leg_thickness),
                     (leg_thickness, leg_thickness), (leg_thickness, leg_length_short),
                     (0, leg_length_short), close=True)
        make_face()
    extrude(amount=bracket_thickness)

solid_body = p.part

inner_edge = solid_body.edges().filter_by(Axis.Z).sort_by(Axis.X)[2]
solid_body = fillet([inner_edge], inner_fillet_radius)

hole_center_x = leg_thickness / 2
hole_center_y = hole_offset_from_inner + hole_diameter / 2
solid_body = solid_body - Pos(hole_center_x, hole_center_y, bracket_thickness/2) * Cylinder(hole_diameter/2, bracket_thickness)

slot_center_x = leg_length_long * 0.6
slot_center_y = leg_thickness / 2
solid_body = solid_body - Pos(slot_center_x, slot_center_y, bracket_thickness/2) * Box(slot_length, slot_width, bracket_thickness)

rib_center_x = leg_thickness / 2
rib_center_y = leg_thickness / 2
solid_body = solid_body + Pos(rib_center_x, rib_center_y, -rib_thickness/2) * Box(rib_width, rib_length, rib_thickness)

part = solid_body
part.name = "L_bracket"
export_step(part, "output.step")