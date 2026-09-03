from build123d import *

base_width = 80.0
base_height = 40.0
arm_width = 30.0
arm_length = 70.0
thickness = 5.0
boss_radius = 12.0
boss_height = 12.0
boss_hole_diameter = 8.0
counterbore_diameter = 14.0
counterbore_depth = 2.5
mount_hole_diameter = 6.0
mount_hole_spacing = 50.0
pocket_width = 30.0
pocket_length = 20.0
pocket_depth = 3.0
chamfer_size = 0.8

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline(
                (-base_width/2, 0),
                (base_width/2, 0),
                (base_width/2, base_height),
                (arm_width/2, base_height),
                (arm_width/2, base_height + arm_length),
                (-arm_width/2, base_height + arm_length),
                (-arm_width/2, base_height),
                (-base_width/2, base_height),
                close=True
            )
        make_face()
    extrude(amount=thickness)

solid_body = p.part

for x in [-mount_hole_spacing/2, mount_hole_spacing/2]:
    solid_body = solid_body - Pos(x, base_height/2, thickness/2) * Cylinder(mount_hole_diameter/2, thickness + 1)

solid_body = solid_body - Pos(0, base_height/2, thickness - pocket_depth/2) * Box(pocket_width, pocket_length, pocket_depth)

boss_center_x = 0
boss_center_y = base_height + arm_length/2
solid_body = solid_body + Pos(boss_center_x, boss_center_y, thickness + boss_height/2) * Cylinder(boss_radius, boss_height)

solid_body = solid_body - Pos(boss_center_x, boss_center_y, thickness + boss_height - counterbore_depth/2) * Cylinder(counterbore_diameter/2, counterbore_depth)

solid_body = solid_body - Pos(boss_center_x, boss_center_y, (thickness + boss_height)/2) * Cylinder(boss_hole_diameter/2, thickness + boss_height + 1)

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = chamfer(top_face.edges(), chamfer_size)

part = solid_body
part.name = "L_bracket_with_boss"
export_step(part, "output.step")