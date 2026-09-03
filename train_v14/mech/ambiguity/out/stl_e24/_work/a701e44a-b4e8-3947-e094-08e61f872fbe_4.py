from build123d import *

leg_height = 70.0
leg_length = 50.0
leg_width = 20.0
thickness = 8.0
rib_width = 6.0
rib_spacing = 10.0
rib_height = 12.0
rib_thickness = 2.0
rib_count = 3
hole_diameter = 5.0
hole_offset_y = 30.0
fillet_radius = 4.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0, 0), (leg_length, 0), (leg_length, leg_height),
                     (leg_length - leg_width, leg_height),
                     (leg_length - leg_width, leg_width),
                     (0, leg_width), close=True)
        make_face()
    extrude(amount=thickness)

solid_body = p.part

for i in range(rib_count):
    x_pos = i * rib_spacing
    rib = Pos(x_pos, 0, rib_thickness / 2) * Box(rib_width, rib_height, rib_thickness)
    solid_body = solid_body + rib

hole = Pos(leg_length, hole_offset_y, thickness / 2) * Cylinder(hole_diameter / 2, thickness)
solid_body = solid_body - hole

z_edges = solid_body.edges().filter_by(Axis.Z)
max_x = max(e.center().X for e in z_edges)
fillet_edges = [e for e in z_edges if abs(e.center().X - max_x) < 0.1]
solid_body = fillet(fillet_edges, fillet_radius)

part = solid_body
part.name = "L_Bracket"
export_step(part, "output.step")