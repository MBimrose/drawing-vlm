from build123d import *

outer_radius = 30.0
step_radius = 20.0
boss_radius = 12.0
base_height = 15.0
step_height = 15.0
boss_height = 20.0
total_height = base_height + step_height + boss_height
fillet_radius = 2.0
mount_hole_dia = 5.0
mount_hole_offset = 20.0
pocket_width = 10.0
pocket_depth = 8.0
pocket_height = 12.0

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            l1 = Line((0, 0), (outer_radius, 0))
            l2 = Line(l1 @ 1, (outer_radius, base_height))
            l3 = Line(l2 @ 1, (step_radius, base_height))
            l4 = Line(l3 @ 1, (step_radius, base_height + step_height))
            l5 = Line(l4 @ 1, (boss_radius, base_height + step_height))
            l6 = Line(l5 @ 1, (boss_radius, total_height))
            l7 = Line(l6 @ 1, (0, total_height))
            l8 = Line(l7 @ 1, (0, 0))
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part
solid_body = fillet(solid_body.edges(), fillet_radius)

for y in [mount_hole_offset, -mount_hole_offset]:
    solid_body = solid_body - Pos(0, y, total_height / 2) * Cylinder(mount_hole_dia / 2, total_height + 10)

pocket = Pos(boss_radius - pocket_depth / 2, 0, total_height - pocket_height / 2) * Box(pocket_depth, pocket_width, pocket_height)
solid_body = solid_body - pocket

part = solid_body
part.name = "stepped_cylinder_with_holes_and_pocket"
export_step(part, "output.step")