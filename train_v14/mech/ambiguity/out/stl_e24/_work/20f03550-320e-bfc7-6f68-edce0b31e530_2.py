from build123d import *

leg_length_horizontal = 80.0
leg_length_vertical = 50.0
leg_thickness = 8.0
bracket_depth = 12.0
fillet_radius = 2.0
hole_diameter = 5.0
hole_spacing = 20.0
hole_offset_from_corner = 15.0
slot_width = 6.0
slot_length = 30.0
slot_offset_from_top = 10.0
rib_width = 6.0
rib_height = 6.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0, 0), (leg_length_horizontal, 0), (leg_length_horizontal, leg_thickness),
                     (leg_thickness, leg_thickness), (leg_thickness, leg_length_vertical + leg_thickness),
                     (0, leg_length_vertical + leg_thickness), close=True)
        make_face()
    extrude(amount=bracket_depth)

solid_body = p.part
solid_body = fillet(solid_body.edges().filter_by(Axis.Z), fillet_radius)

for i in range(3):
    x = hole_offset_from_corner + i * hole_spacing
    y = leg_thickness / 2
    solid_body = solid_body - Pos(x, y, bracket_depth / 2) * Cylinder(hole_diameter / 2, bracket_depth)

slot_center_x = leg_thickness / 2
slot_center_y = leg_length_vertical + leg_thickness - slot_offset_from_top - slot_length / 2
solid_body = solid_body - Pos(slot_center_x, slot_center_y, bracket_depth * 3 / 4) * Box(slot_width, slot_length, bracket_depth / 2)

rib = Pos(leg_thickness / 2, leg_thickness / 2, bracket_depth / 2) * Box(rib_width, rib_height, bracket_depth)
solid_body = solid_body + rib

part = solid_body
part.name = "L_bracket"
export_step(part, "output.step")