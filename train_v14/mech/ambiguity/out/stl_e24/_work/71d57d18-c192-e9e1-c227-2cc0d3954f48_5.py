from build123d import *

outer_radius = 30.0
inner_radius = 12.0
spacer_height = 20.0
top_fillet_radius = 4.0
bottom_chamfer = 2.0
mount_hole_diameter = 4.0
mount_hole_spacing = 36.0
boss_radius = 4.0
boss_height = 6.0
pocket_width = 10.0
pocket_depth = 5.0
pocket_offset = 8.0

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            l1 = Line((outer_radius, 0), (outer_radius, spacer_height - top_fillet_radius))
            l2 = ThreePointArc(l1 @ 1, (outer_radius - top_fillet_radius, spacer_height), (inner_radius, spacer_height))
            l3 = Line(l2 @ 1, (inner_radius, 0))
            l4 = Line(l3 @ 1, (outer_radius, 0))
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part
solid_body = solid_body - Cylinder(inner_radius, spacer_height * 2)

bottom_face = solid_body.faces().sort_by(Axis.Z)[0]
solid_body = chamfer(bottom_face.edges(), bottom_chamfer)

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = fillet(top_face.edges(), top_fillet_radius)

for x in [-mount_hole_spacing / 2, mount_hole_spacing / 2]:
    solid_body = solid_body - Pos(x, 0, 0) * Cylinder(mount_hole_diameter / 2, spacer_height * 2)

boss = Pos(inner_radius + boss_height / 2, 0, 0) * Rot(0, 90, 0) * Cylinder(boss_radius, boss_height)
solid_body = solid_body + boss

pocket = Pos(pocket_offset, 0, spacer_height - pocket_depth / 2) * Box(pocket_width, pocket_depth, pocket_depth)
solid_body = solid_body - pocket

part = solid_body
part.name = "spacer_with_boss_and_pocket"
export_step(part, "output.step")