from build123d import *

outer_radius = 30.0
wall_thickness = 5.0
inner_radius = outer_radius - wall_thickness
length = 80.0
boss_radius = 10.0
boss_height = 6.0
boss_offset = 15.0
chamfer_size = 2.0
mount_hole_dia = 5.0
mount_hole_spacing = 40.0
groove_width = 4.0
groove_depth = 2.0
groove_offset = 10.0

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            l1 = Line((inner_radius, 0), (outer_radius, 0))
            l2 = Line(l1@1, (outer_radius, length))
            l3 = Line(l2@1, (inner_radius, length))
            l4 = Line(l3@1, (inner_radius, 0))
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
top_edges = top_face.edges()
solid_body = chamfer(top_edges, chamfer_size)

boss = Pos(outer_radius + boss_height/2, 0, boss_offset) * Rot(0, 90, 0) * Cylinder(boss_radius, boss_height)
solid_body = solid_body + boss

for x in [-mount_hole_spacing/2, mount_hole_spacing/2]:
    hole = Pos(x, 0, length/2) * Cylinder(mount_hole_dia/2, length + 20)
    solid_body = solid_body - hole

groove = Pos(0, 0, length - groove_offset - groove_depth/2) * Cylinder(inner_radius - groove_width/2, groove_depth)
solid_body = solid_body - groove

part = solid_body
part.name = "hollow_cylinder_with_boss"
export_step(part, "output.step")