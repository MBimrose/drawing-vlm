from build123d import *
import math

outer_diameter = 80.0
inner_diameter = 30.0
boss_height = 20.0
body_height = 25.0
fillet_radius = 4.0
central_hole_diameter = 12.0
mount_hole_diameter = 5.0
mount_hole_angle = 60.0
mount_hole_radius = 40.0
pocket_width = 30.0
pocket_length = 20.0
pocket_depth = 5.0

total_height = boss_height + body_height

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            l1 = Line((0, 0), (inner_diameter/2, 0))
            l2 = Line(l1@1, (inner_diameter/2, boss_height))
            l3 = Line(l2@1, (outer_diameter/2, boss_height))
            l4 = Line(l3@1, (outer_diameter/2, total_height))
            l5 = Line(l4@1, (0, total_height))
            l6 = Line(l5@1, (0, 0))
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part
solid_body = fillet(solid_body.edges(), fillet_radius)

solid_body = solid_body - Pos(0, 0, total_height/2) * Cylinder(central_hole_diameter/2, total_height + 10)

for i in range(2):
    angle = math.radians(i * mount_hole_angle)
    px = mount_hole_radius * math.cos(angle)
    py = mount_hole_radius * math.sin(angle)
    solid_body = solid_body - Pos(px, py, total_height/2) * Cylinder(mount_hole_diameter/2, total_height + 10)

solid_body = solid_body - Pos(0, 0, total_height - pocket_depth/2) * Box(pocket_width, pocket_length, pocket_depth)

part = solid_body
part.name = "revolved_body_with_holes_and_pocket"
export_step(part, "output.step")