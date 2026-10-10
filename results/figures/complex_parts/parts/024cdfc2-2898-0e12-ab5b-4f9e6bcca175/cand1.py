from build123d import *
import math

outer_radius = 30.0
inner_radius = 12.0
height = 20.0
fillet_radius = 2.0
keyway_width = 8.0
keyway_depth = 6.0
rib_count = 6
rib_width = 4.0
rib_height = 10.0
rib_thickness = 2.0
boss_radius = 5.0
boss_height = 5.0

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            l1 = Line((inner_radius, 0), (inner_radius, height))
            l2 = Line(l1 @ 1, (outer_radius, height))
            l3 = Line(l2 @ 1, (outer_radius, 0))
            l4 = Line(l3 @ 1, (inner_radius, 0))
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part
solid_body = fillet(solid_body.edges(), fillet_radius)

keyway = Pos(outer_radius - keyway_depth / 2, 0, height / 2) * Box(keyway_depth, keyway_width, height)
solid_body = solid_body - keyway

for i in range(rib_count):
    angle = i * 360.0 / rib_count
    rib = Rot(0, 0, angle) * Pos(inner_radius + rib_thickness / 2, 0, 0) * Box(rib_thickness, rib_width, rib_height)
    solid_body = solid_body + rib

boss = Pos(outer_radius, 0, boss_height / 2) * Cylinder(boss_radius, boss_height)
solid_body = solid_body + boss

part = solid_body
part.name = "revolved_ring_with_keyway_ribs_boss"
export_step(part, "output.step")