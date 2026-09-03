from build123d import *

horizontal_leg_length = 80.0
vertical_leg_length = 60.0
leg_thickness = 10.0
bracket_thickness = 10.0
inner_chamfer = 2.0
blind_hole_diameter = 6.0
blind_hole_depth = 30.0
blind_hole_offset_from_top = 15.0
mount_hole_diameter = 5.0
mount_hole_spacing = 20.0
mount_hole_offset_from_end = 15.0
rib_width = 6.0
rib_height = 30.0
rib_thickness = 4.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0, 0), (horizontal_leg_length, 0), (horizontal_leg_length, leg_thickness),
                     (leg_thickness, leg_thickness), (leg_thickness, vertical_leg_length),
                     (0, vertical_leg_length), close=True)
        make_face()
    extrude(amount=bracket_thickness)

solid_body = p.part

inner_edge = [e for e in solid_body.edges().filter_by(Axis.Z) if abs(e.center().X - leg_thickness) < 0.1 and abs(e.center().Y - leg_thickness) < 0.1][0]
solid_body = chamfer([inner_edge], inner_chamfer)

blind_hole = Pos(leg_thickness/2, vertical_leg_length - blind_hole_depth/2, bracket_thickness/2) * Rot(90, 0, 0) * Cylinder(blind_hole_diameter/2, blind_hole_depth)
solid_body = solid_body - blind_hole

for i in range(3):
    x = mount_hole_offset_from_end + i * mount_hole_spacing
    y = leg_thickness / 2
    solid_body = solid_body - Pos(x, y, bracket_thickness) * Cylinder(mount_hole_diameter/2, bracket_thickness)

rib = Pos(leg_thickness/2, vertical_leg_length/2, bracket_thickness/2) * Box(rib_width, rib_height, rib_thickness)
solid_body = solid_body + rib

part = solid_body
part.name = "L_bracket"
export_step(part, "output.step")