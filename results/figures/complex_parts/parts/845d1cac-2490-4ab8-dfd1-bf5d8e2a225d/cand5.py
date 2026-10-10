from build123d import *

arm_length = 80.0
arm_width_base = 12.0
arm_width_tip = 4.0
arm_thickness = 6.0
boss_diameter = 12.0
boss_height = 20.0
mount_hole_diameter = 5.0
mount_hole_spacing = 30.0
pocket_width = 15.0
pocket_depth = 4.0
chamfer_size = 0.5

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0, -arm_width_base/2), (arm_length*0.6, -arm_width_base/2),
                     (arm_length, -arm_width_tip/2), (arm_length, arm_width_tip/2),
                     (arm_length*0.6, arm_width_base/2), (0, arm_width_base/2), close=True)
        make_face()
    extrude(amount=arm_thickness)

solid_body = p.part

for x, y in [(mount_hole_spacing/2, 0), (-mount_hole_spacing/2, 0)]:
    solid_body = solid_body - Pos(x, y, arm_thickness/2) * Cylinder(mount_hole_diameter/2, arm_thickness + 1)

pocket_center_x = arm_length * 0.5
pocket_center_y = 0
solid_body = solid_body - Pos(pocket_center_x, pocket_center_y, arm_thickness - pocket_depth/2) * Box(pocket_width, pocket_depth, pocket_depth)

boss_center_x = arm_length
boss_center_y = 0
solid_body = solid_body + Pos(boss_center_x, boss_center_y, 0) * Rot(0, 90, 0) * Cylinder(boss_diameter/2, boss_height)

z_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = chamfer(z_edges, chamfer_size)

part = solid_body
part.name = "tapered_arm_with_boss"
export_step(part, "output.step")