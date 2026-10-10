from build123d import *

outer_radius = 30.0
wall_thickness = 5.0
inner_radius = outer_radius - wall_thickness
height = 80.0
chamfer_size = 2.0
groove_depth = 2.0
groove_width = 4.0
groove_position = height * 0.5
boss_radius = 10.0
boss_height = 20.0
boss_offset_z = 10.0

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            l1 = Line((inner_radius, 0), (inner_radius, height - chamfer_size))
            l2 = Line(l1@1, (inner_radius + chamfer_size, height))
            l3 = Line(l2@1, (outer_radius - chamfer_size, height))
            l4 = Line(l3@1, (outer_radius, height - chamfer_size))
            l5 = Line(l4@1, (outer_radius, 0))
            l6 = Line(l5@1, (inner_radius, 0))
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part

groove_cyl = Pos(0, 0, groove_position - groove_width / 2) * Cylinder(inner_radius - groove_depth, groove_width)
solid_body = solid_body - groove_cyl

boss_cyl = Pos(outer_radius + boss_height / 2, 0, boss_offset_z) * Rot(0, 90, 0) * Cylinder(boss_radius, boss_height)
solid_body = solid_body + boss_cyl

part = solid_body
part.name = "revolved_cup_with_groove_and_boss"
export_step(part, "output.step")