from build123d import *

outer_radius = 30
wall_thickness = 5
inner_radius = outer_radius - wall_thickness
length = 80
boss_radius = 10
boss_height = 6
boss_offset = 15
chamfer_size = 2
mount_hole_dia = 5
mount_hole_spacing = 30
pocket_width = 20
pocket_height = 10
pocket_depth = 4

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            l1 = Line((inner_radius, 0), (inner_radius, length))
            l2 = Line(l1@1, (outer_radius, length))
            l3 = Line(l2@1, (outer_radius, 0))
            l4 = Line(l3@1, (inner_radius, 0))
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = chamfer(top_face.edges(), chamfer_size)

boss = Pos(outer_radius + boss_height/2, 0, boss_offset) * Rot(0, 90, 0) * Cylinder(boss_radius, boss_height)
solid_body = solid_body + boss

pocket = Pos(outer_radius - pocket_depth/2, 0, length - 30) * Box(pocket_depth, pocket_width, pocket_height)
solid_body = solid_body - pocket

for x in [-mount_hole_spacing/2, mount_hole_spacing/2]:
    hole = Pos(x, 0, length/2) * Cylinder(mount_hole_dia/2, length + 20)
    solid_body = solid_body - hole

part = solid_body
part.name = "hollow_cylinder_with_boss_pocket_holes"
export_step(part, "output.step")