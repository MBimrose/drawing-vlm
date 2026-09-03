from build123d import *

arm_length = 80.0
arm_width = 20.0
arm_thickness = 25.0
wall_thickness = 2.0
rib_width = 10.0
rib_height = 5.0
rib_thickness = 3.0
blind_hole_diameter = 6.0
blind_hole_depth = 15.0
mount_hole_diameter = 4.0
mount_hole_spacing = 30.0
mount_hole_offset = 15.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            l1 = Line((-arm_length/2 + 10, -arm_width/2), (arm_length/2 - 10, -arm_width/2))
            a1 = ThreePointArc(l1 @ 1, (arm_length/2, 0), (arm_length/2 - 10, arm_width/2))
            l2 = Line(a1 @ 1, (-arm_length/2 + 10, arm_width/2))
            a2 = ThreePointArc(l2 @ 1, (-arm_length/2, 0), (-arm_length/2 + 10, -arm_width/2))
        make_face()
    extrude(amount=arm_thickness)

solid_body = p.part
solid_body = offset(solid_body, amount=-wall_thickness)

rib = Pos(0, 0, arm_thickness - rib_thickness/2) * Box(rib_width, rib_height, rib_thickness)
solid_body = solid_body + rib

blind_hole = Pos(0, 0, arm_thickness - blind_hole_depth/2) * Cylinder(blind_hole_diameter/2, blind_hole_depth)
solid_body = solid_body - blind_hole

for x in [mount_hole_offset, mount_hole_offset + mount_hole_spacing]:
    mount_hole = Pos(x, 0, arm_thickness/2) * Rot(90, 0, 0) * Cylinder(mount_hole_diameter/2, arm_width + 10)
    solid_body = solid_body - mount_hole

part = solid_body
part.name = "arm_with_rib_and_holes"
export_step(part, "output.step")