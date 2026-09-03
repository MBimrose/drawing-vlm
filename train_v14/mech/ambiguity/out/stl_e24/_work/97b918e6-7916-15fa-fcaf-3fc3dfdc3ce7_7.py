from build123d import *

vertical_leg_length = 80.0
horizontal_leg_length = 60.0
leg_thickness = 12.0
inner_fillet_radius = 2.0
through_hole_diameter = 6.0
mount_hole_diameter = 5.0
mount_hole_spacing = 20.0
mount_hole_offset = 15.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            l1 = Line((0, 0), (0, vertical_leg_length))
            l2 = Line(l1 @ 1, (leg_thickness, vertical_leg_length))
            l3 = Line(l2 @ 1, (leg_thickness, leg_thickness))
            l4 = Line(l3 @ 1, (horizontal_leg_length, leg_thickness))
            l5 = Line(l4 @ 1, (horizontal_leg_length, 0))
            l6 = Line(l5 @ 1, (0, 0))
        make_face()
    extrude(amount=leg_thickness)

solid_body = p.part

inner_edges = [e for e in solid_body.edges().filter_by(Axis.Z) if abs(e.center().X - leg_thickness) < 0.1 and abs(e.center().Y - leg_thickness) < 0.1]
solid_body = fillet(inner_edges, inner_fillet_radius)

solid_body = solid_body - Pos(horizontal_leg_length / 2, leg_thickness / 2, leg_thickness / 2) * Cylinder(through_hole_diameter / 2, leg_thickness)

for i in range(3):
    y_pos = mount_hole_offset + i * mount_hole_spacing
    solid_body = solid_body - Pos(leg_thickness / 2, y_pos, leg_thickness / 2) * Cylinder(mount_hole_diameter / 2, leg_thickness)

part = solid_body
part.name = "L_Bracket"
export_step(part, "output.step")