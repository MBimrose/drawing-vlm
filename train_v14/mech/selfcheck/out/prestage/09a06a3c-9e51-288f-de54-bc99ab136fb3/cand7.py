from build123d import *

knob_length = 70.0
knob_height = 25.0
knob_radius = 12.0
wall_thickness = 2.0
pocket_width = 12.0
pocket_height = 8.0
pocket_depth = 4.0
blind_hole_diameter = 6.0
blind_hole_depth = 15.0
mount_hole_diameter = 4.0
mount_hole_spacing = 30.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            l1 = Line((-knob_length/2 + knob_radius, -knob_height/2), (knob_length/2 - knob_radius, -knob_height/2))
            a1 = ThreePointArc(l1 @ 1, (knob_length/2, 0), (knob_length/2 - knob_radius, knob_height/2))
            l2 = Line(a1 @ 1, (-knob_length/2 + knob_radius, knob_height/2))
            a2 = ThreePointArc(l2 @ 1, (-knob_length/2, 0), (-knob_length/2 + knob_radius, -knob_height/2))
        make_face()
    extrude(amount=knob_radius * 2)

solid_body = p.part
solid_body = offset(solid_body, amount=-wall_thickness)

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
top_center = top_face.center()

pocket = Pos(top_center.X, top_center.Y, top_center.Z) * Box(pocket_width, pocket_height, pocket_depth)
solid_body = solid_body - pocket

blind_hole = Pos(top_center.X, top_center.Y, top_center.Z - blind_hole_depth/2) * Cylinder(blind_hole_diameter/2, blind_hole_depth)
solid_body = solid_body - blind_hole

right_face = solid_body.faces().sort_by(Axis.X)[-1]
right_center = right_face.center()

for i in range(2):
    x_offset = (i - 0.5) * mount_hole_spacing
    hole = Pos(right_center.X + x_offset, right_center.Y, right_center.Z) * Rot(90, 0, 0) * Cylinder(mount_hole_diameter/2, knob_radius * 4)
    solid_body = solid_body - hole

part = solid_body
part.name = "knob"
export_step(part, "output.step")