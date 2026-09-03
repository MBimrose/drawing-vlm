from build123d import *

leg_length = 80.0
leg_height = 70.0
leg_thickness = 12.0
bracket_thickness = 8.0
slot_width = 6.0
slot_length = 20.0
slot_depth = 4.0
hole_diameter = 4.5
hole_spacing = 10.0
hole_offset_from_bottom = 15.0
fillet_radius = 2.0
rib_width = 8.0
rib_height = 6.0
rib_offset = 5.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0, 0), (leg_length, 0), (leg_length, leg_height),
                     (leg_length - leg_thickness, leg_height),
                     (leg_length - leg_thickness, leg_thickness),
                     (0, leg_thickness), close=True)
        make_face()
    extrude(amount=bracket_thickness)

solid_body = p.part

inner_edges = solid_body.edges().filter_by(Axis.Z)
inner_edge = min(inner_edges, key=lambda e: (e.center().X - leg_thickness)**2 + (e.center().Y - leg_thickness)**2)
solid_body = fillet([inner_edge], fillet_radius)

slot_center_x = leg_length - leg_thickness / 2
slot_center_y = leg_height / 2
slot_cut = Pos(slot_center_x, slot_center_y, bracket_thickness - slot_depth/2) * Box(slot_width, slot_length, slot_depth)
solid_body = solid_body - slot_cut

hole_x = leg_length - leg_thickness / 2
for i in range(3):
    hole_y = hole_offset_from_bottom + i * hole_spacing
    hole_cut = Pos(hole_x, hole_y, bracket_thickness/2) * Cylinder(hole_diameter/2, bracket_thickness + 2)
    solid_body = solid_body - hole_cut

rib_center_x = rib_offset + rib_width / 2
rib_center_y = leg_thickness / 2
rib = Pos(rib_center_x, rib_center_y, bracket_thickness + rib_height/2) * Box(rib_width, rib_height, rib_height)
solid_body = solid_body + rib

part = solid_body
part.name = "L_bracket"
export_step(part, "output.step")