from build123d import *

horizontal_length = 80.0
vertical_length = 70.0
leg_width = 20.0
thickness = 8.0
fillet_radius = 4.0
hole_diameter = 6.0
hole_offset_x = 30.0
hole_offset_y = 35.0
slot_width = 12.0
slot_length = 30.0
slot_offset_x = 15.0
slot_offset_y = 10.0
rib_width = 6.0
rib_height = 12.0
rib_thickness = 2.0
rib_spacing = 8.0
rib_count = 3

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0, 0), (horizontal_length, 0), (horizontal_length, leg_width),
                     (horizontal_length - thickness, leg_width),
                     (horizontal_length - thickness, vertical_length),
                     (horizontal_length - 2*thickness, vertical_length),
                     (horizontal_length - 2*thickness, leg_width),
                     (0, leg_width), close=True)
        make_face()
    extrude(amount=thickness)

solid_body = p.part

inner_edges = solid_body.edges().filter_by(Axis.Z).sort_by(Axis.X)[-2:]
solid_body = fillet(inner_edges, fillet_radius)

solid_body = solid_body - Pos(hole_offset_x, hole_offset_y, thickness/2) * Cylinder(hole_diameter/2, thickness)
solid_body = solid_body - Pos(slot_offset_x, slot_offset_y, thickness/2) * Box(slot_width, slot_length, thickness)

for i in range(rib_count):
    x_pos = rib_spacing * (i + 1)
    solid_body = solid_body - Pos(x_pos, leg_width/2, rib_thickness/2) * Box(rib_width, rib_height, rib_thickness)

part = solid_body
part.name = "L_Bracket"
export_step(part, "output.step")