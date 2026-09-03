from build123d import *

arm_length = 80.0
arm_width = 30.0
arm_thickness = 10.0
v_groove_depth = 6.0
v_groove_width = 12.0
blind_hole_diameter = 20.0
blind_hole_depth = 8.0
chamfer_distance = 1.0
mount_hole_diameter = 4.0
mount_hole_spacing = 15.0
mount_hole_offset = 20.0

solid_body = Pos(0, 0, arm_thickness/2) * Box(arm_length, arm_width, arm_thickness)

with BuildPart() as gp:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            Line((-v_groove_width/2, 0), (0, -v_groove_depth))
            Line((0, -v_groove_depth), (v_groove_width/2, 0))
            Line((v_groove_width/2, 0), (-v_groove_width/2, 0))
        make_face()
    extrude(amount=arm_length)
groove = Pos(0, 0, arm_thickness/2) * gp.part
solid_body = solid_body - groove

blind_hole = Pos(arm_length/2 - 10, 0, blind_hole_depth/2) * Cylinder(blind_hole_diameter/2, blind_hole_depth)
solid_body = solid_body - blind_hole

left_edges = solid_body.edges().filter_by(Axis.Z).sort_by(Axis.X)[:2]
solid_body = chamfer(left_edges, chamfer_distance)

for y in [-mount_hole_spacing/2, mount_hole_spacing/2]:
    hole = Pos(-arm_length/2 + mount_hole_offset, y, arm_thickness/2) * Cylinder(mount_hole_diameter/2, arm_thickness)
    solid_body = solid_body - hole

part = solid_body
part.name = "arm_with_groove_and_holes"
export_step(part, "output.step")