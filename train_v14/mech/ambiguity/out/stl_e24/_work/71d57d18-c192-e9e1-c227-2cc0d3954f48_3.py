from build123d import *

outer_radius = 30.0
inner_radius = 12.0
height = 20.0
top_fillet_radius = 5.0
bottom_chamfer = 2.0
slot_width = 6.0
slot_height = 10.0
slot_depth = 8.0
mount_hole_dia = 4.0
mount_hole_offset = 18.0
boss_radius = 4.0
boss_height = 8.0

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            l1 = Line((inner_radius, 0), (outer_radius, 0))
            l2 = Line(l1@1, (outer_radius, height - top_fillet_radius))
            a1 = ThreePointArc(l2@1, (outer_radius - top_fillet_radius, height), (inner_radius, height))
            l3 = Line(a1@1, (inner_radius, 0))
        make_face()
    revolve(axis=Axis.Z)

solid = p.part

bottom_face = solid.faces().sort_by(Axis.Z)[0]
solid = chamfer(bottom_face.edges(), bottom_chamfer)

slot = Pos(0, 0, height/2) * Box(slot_width, slot_height, slot_depth)
solid = solid - slot

for x, y in [(-mount_hole_offset, 0), (mount_hole_offset, 0)]:
    solid = solid - Pos(x, y, height/2) * Cylinder(mount_hole_dia/2, height + 10)

boss = Pos(inner_radius + boss_radius, 0, 0) * Rot(0, 90, 0) * Cylinder(boss_radius, boss_height)
solid = solid + boss

part = solid
part.name = "knob"
export_step(part, "output.step")