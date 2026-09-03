from build123d import *

outer_radius = 30.0
inner_radius = 12.0
knob_height = 20.0
fillet_radius = 5.0
chamfer_distance = 2.0
mount_hole_diameter = 4.0
mount_hole_offset = 18.0
pocket_width = 12.0
pocket_depth = 6.0
pocket_height = 8.0
boss_radius = 4.0
boss_height = 6.0

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            l1 = Line((inner_radius, 0), (outer_radius, 0))
            l2 = Line(l1@1, (outer_radius, knob_height - fillet_radius))
            a1 = ThreePointArc(l2@1, (outer_radius - fillet_radius, knob_height), (inner_radius, knob_height))
            l3 = Line(a1@1, (inner_radius, 0))
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = fillet(top_face.edges(), fillet_radius)

bottom_face = solid_body.faces().sort_by(Axis.Z)[0]
solid_body = chamfer(bottom_face.edges(), chamfer_distance)

for x, y in [(-mount_hole_offset, 0), (mount_hole_offset, 0)]:
    solid_body = solid_body - Pos(x, y, knob_height/2) * Cylinder(mount_hole_diameter/2, knob_height + 10)

solid_body = solid_body - Pos(outer_radius - pocket_depth/2, 0, knob_height/2) * Box(pocket_depth, pocket_width, pocket_height)

solid_body = solid_body + Pos(inner_radius + boss_height/2, 0, 0) * Rot(0, 90, 0) * Cylinder(boss_radius, boss_height)

part = solid_body
part.name = "knob"
export_step(part, "output.step")