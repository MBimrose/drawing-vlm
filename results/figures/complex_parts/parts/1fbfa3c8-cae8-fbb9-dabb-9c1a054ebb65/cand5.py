from build123d import *
import math

outer_radius = 30.0
flange_thickness = 10.0
boss_radius = 20.0
boss_height = 15.0
bore_radius = 8.0
mount_hole_diameter = 5.0
mount_hole_count = 6
mount_hole_radius = 25.0
keyway_width = 6.0
keyway_depth = 4.0
keyway_offset = 12.0
chamfer_size = 1.0

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            l1 = Line((0, 0), (outer_radius, 0))
            l2 = Line(l1 @ 1, (outer_radius, flange_thickness))
            l3 = Line(l2 @ 1, (boss_radius, flange_thickness))
            l4 = Line(l3 @ 1, (boss_radius, flange_thickness + boss_height))
            l5 = Line(l4 @ 1, (0, flange_thickness + boss_height))
            l6 = Line(l5 @ 1, (0, 0))
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part

total_height = flange_thickness + boss_height
solid_body = solid_body - Pos(0, 0, total_height / 2) * Cylinder(bore_radius, total_height + 1)

for i in range(mount_hole_count):
    angle = math.radians(i * 360.0 / mount_hole_count)
    px = mount_hole_radius * math.cos(angle)
    py = mount_hole_radius * math.sin(angle)
    solid_body = solid_body - Pos(px, py, total_height / 2) * Cylinder(mount_hole_diameter / 2, total_height + 1)

solid_body = solid_body - Pos(keyway_offset, 0, total_height - keyway_depth / 2) * Box(keyway_width, keyway_depth, keyway_depth)

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = chamfer(top_face.edges(), chamfer_size)

part = solid_body
part.name = "flange_with_boss"
export_step(part, "output.step")