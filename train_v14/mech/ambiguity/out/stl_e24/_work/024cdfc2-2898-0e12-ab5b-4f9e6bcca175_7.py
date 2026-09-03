from build123d import *
import math

outer_radius = 30.0
inner_radius = 12.0
height = 20.0
fillet_radius = 2.0
slot_width = 6.0
slot_depth = 8.0
rib_width = 4.0
rib_height = 12.0
rib_count = 6
boss_radius = 5.0
boss_height = 4.0

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            l1 = Line((inner_radius, 0), (outer_radius, 0))
            l2 = Line(l1@1, (outer_radius, height))
            l3 = Line(l2@1, (inner_radius, height))
            l4 = Line(l3@1, (inner_radius, 0))
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part
solid_body = fillet(solid_body.edges(), fillet_radius)

slot_box = Pos(outer_radius - slot_depth/2, 0, height/2) * Box(slot_depth, slot_width, height)
solid_body = solid_body - slot_box

boss_cyl = Pos(outer_radius, 0, boss_height/2) * Cylinder(boss_radius, boss_height)
solid_body = solid_body + boss_cyl

for i in range(rib_count):
    angle = i * 360.0 / rib_count
    rib = Rot(0, 0, angle) * Pos(inner_radius + rib_width/2, 0, rib_height/2) * Box(rib_width, rib_height, rib_height)
    solid_body = solid_body + rib

part = solid_body
part.name = "revolved_ring_with_slot_boss_ribs"
export_step(part, "output.step")