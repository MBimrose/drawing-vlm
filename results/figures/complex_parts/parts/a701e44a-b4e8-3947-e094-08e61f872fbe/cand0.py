from build123d import *
import math

leg_length = 80.0
leg_width = 20.0
thickness = 8.0
vertical_height = 70.0
fillet_radius = 4.0
hole_diameter = 5.0
countersink_diameter = 9.0
countersink_angle = 82.0
hole_offset_from_top = 15.0
rib_width = 6.0
rib_height = 12.0
rib_spacing = 8.0
rib_count = 3

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0, 0), (leg_length, 0), (leg_length, leg_width),
                     (leg_length - thickness, leg_width),
                     (leg_length - thickness, vertical_height),
                     (leg_length - 2*thickness, vertical_height),
                     (leg_length - 2*thickness, leg_width),
                     (0, leg_width), close=True)
        make_face()
    extrude(amount=thickness)

solid_body = p.part

z_edges = solid_body.edges().filter_by(Axis.Z)
max_x = max(e.center().X for e in z_edges)
fillet_edges = [e for e in z_edges if abs(e.center().X - max_x) < 0.1]
solid_body = fillet(fillet_edges, fillet_radius)

hole_center_x = leg_length - thickness / 2
hole_center_y = vertical_height - hole_offset_from_top
shaft_r = hole_diameter / 2
csk_r = countersink_diameter / 2
csk_h = (csk_r - shaft_r) / math.tan(math.radians(countersink_angle / 2))
shaft = Pos(hole_center_x, hole_center_y, thickness/2) * Cylinder(shaft_r, thickness)
csk_cone = Pos(hole_center_x, hole_center_y, thickness - csk_h/2) * Cone(shaft_r, csk_r, csk_h)
solid_body = solid_body - shaft - csk_cone

for i in range(rib_count):
    x_pos = leg_length / 2 - (rib_count - 1) * rib_spacing / 2 + i * rib_spacing
    rib = Pos(x_pos, 0, thickness/4) * Box(rib_width, rib_height, thickness/2)
    solid_body = solid_body + rib

part = solid_body
part.name = "L_bracket_with_ribs"
export_step(part, "output.step")