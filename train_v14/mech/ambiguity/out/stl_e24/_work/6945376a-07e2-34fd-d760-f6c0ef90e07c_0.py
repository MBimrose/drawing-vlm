from build123d import *

horizontal_length = 80.0
vertical_height = 60.0
leg_thickness = 12.0
bracket_thickness = 8.0
inner_fillet_radius = 2.0
hole_diameter = 4.5
hole_spacing = 10.0
hole_offset_from_top = 15.0
slot_width = 6.0
slot_length = 20.0
slot_offset_from_top = 25.0
rib_width = 8.0
rib_depth = 6.0
rib_height = 4.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0, 0), (horizontal_length, 0), (horizontal_length, vertical_height + leg_thickness),
                     (horizontal_length - leg_thickness, vertical_height + leg_thickness),
                     (horizontal_length - leg_thickness, leg_thickness), (0, leg_thickness), close=True)
        make_face()
    extrude(amount=bracket_thickness)

solid_body = p.part

inner_edges = solid_body.edges().filter_by(Axis.Z).sort_by(Axis.X)[1:2]
solid_body = fillet(inner_edges, inner_fillet_radius)

hole_x = horizontal_length - leg_thickness / 2
for i in range(3):
    hole_y = vertical_height + leg_thickness - hole_offset_from_top - i * hole_spacing
    solid_body = solid_body - Pos(hole_x, hole_y, bracket_thickness / 2) * Cylinder(hole_diameter / 2, bracket_thickness)

slot_x = horizontal_length - leg_thickness / 2
slot_y = vertical_height + leg_thickness - slot_offset_from_top
solid_body = solid_body - Pos(slot_x, slot_y, bracket_thickness - bracket_thickness / 4) * Box(slot_width, slot_length, bracket_thickness / 2)

rib_x = leg_thickness / 2
rib_y = leg_thickness / 2
solid_body = solid_body + Pos(rib_x, rib_y, bracket_thickness + rib_height / 2) * Box(rib_width, rib_depth, rib_height)

part = solid_body
part.name = "L_Bracket"
export_step(part, "output.step")