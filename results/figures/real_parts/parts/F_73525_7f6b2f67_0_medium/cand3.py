from build123d import *
import math

outer_diameter = 80.0
inner_diameter = 70.0
thickness = 20.0
wall_thickness = 4.0
boss_diameter = 12.0
boss_height = 8.0
rib_width = 6.0
rib_height = 12.0
rib_thickness = 3.0
mount_hole_diameter = 5.0
mount_hole_radius = 30.0
chamfer_distance = 1.0
pocket_depth = 2.0
pocket_diameter = 30.0

outer_radius = outer_diameter / 2.0
inner_radius = inner_diameter / 2.0
boss_radius = boss_diameter / 2.0

with BuildPart() as p:
    with BuildSketch(Plane.XY) as sk:
        with BuildLine() as bl:
            l1 = Line((0, inner_radius), (thickness, inner_radius))
            l2 = Line(l1 @ 1, (thickness, outer_radius))
            l3 = Line(l2 @ 1, (0, outer_radius))
            l4 = Line(l3 @ 1, (0, inner_radius))
        make_face()
    revolve(axis=Axis.X)

solid_body = p.part
solid_body = solid_body + Pos(thickness + boss_height / 2, 0, 0) * Rot(0, 90, 0) * Cylinder(boss_radius, boss_height)

for i in range(4):
    angle = i * 90
    rib = Rot(angle, 0, 0) * Pos(thickness / 2, inner_radius + rib_thickness / 2, 0) * Box(thickness, rib_thickness, rib_width)
    solid_body = solid_body + rib

for i in range(4):
    theta = math.radians(i * 90)
    x = mount_hole_radius * math.cos(theta)
    y = mount_hole_radius * math.sin(theta)
    solid_body = solid_body - Pos(x, y, 0) * Cylinder(mount_hole_diameter / 2, thickness + 2)

solid_body = solid_body - Pos(thickness / 2, 0, 0) * Cylinder(pocket_diameter / 2, pocket_depth)
solid_body = chamfer(solid_body.edges().filter_by(Axis.X), chamfer_distance)

part = solid_body
part.name = "ring_with_boss_ribs"
export_step(part, "output.step")