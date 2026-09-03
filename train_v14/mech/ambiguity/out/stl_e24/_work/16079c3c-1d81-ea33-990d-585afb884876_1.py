from build123d import *

arm_length = 80.0
arm_width = 30.0
arm_thickness = 6.0
boss_diameter = 12.0
boss_height = 8.0
fillet_radius = 1.0
chamfer_distance = 0.7
mount_hole_diameter = 4.0
mount_hole_offset = 10.0
rib_width = 10.0
rib_height = 4.0
rib_depth = 2.0

with BuildPart() as p:
    with BuildSketch() as s:
        Rectangle(arm_width, arm_thickness)
    extrude(amount=arm_length)

solid_body = p.part

vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = fillet(vertical_edges, fillet_radius)

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
top_edges = top_face.edges()
solid_body = chamfer(top_edges, chamfer_distance)

boss = Pos(0, arm_thickness/2, 0) * Rot(90, 0, 0) * Cylinder(boss_diameter/2, boss_height)
solid_body = solid_body + boss

for x, y in [(-arm_length/2 + mount_hole_offset, 0), (arm_length/2 - mount_hole_offset, 0)]:
    hole = Pos(x, y, arm_length/2) * Cylinder(mount_hole_diameter/2, arm_length + 10)
    solid_body = solid_body - hole

rib_cut = Pos(0, 0, arm_length - rib_depth/2) * Box(rib_width, rib_height, rib_depth)
solid_body = solid_body - rib_cut

part = solid_body
part.name = "arm_with_boss_and_ribs"
export_step(part, "output.step")