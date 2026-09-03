from build123d import *

outer_radius = 30.0
wall_thickness = 3.0
inner_radius = outer_radius - wall_thickness
tube_length = 80.0
boss_radius = 6.0
boss_height = 10.0
boss_center_z = 0.0
boss_offset = inner_radius + boss_height / 2.0
thread_hole_radius = 3.0
thread_hole_depth = boss_height + 2.0
chamfer_size = 0.5
relief_width = 12.0
relief_height = 8.0
relief_depth = 2.0

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            Line((inner_radius, -tube_length/2), (outer_radius, -tube_length/2))
            Line((outer_radius, -tube_length/2), (outer_radius, tube_length/2))
            Line((outer_radius, tube_length/2), (inner_radius, tube_length/2))
            Line((inner_radius, tube_length/2), (inner_radius, -tube_length/2))
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part
boss = Pos(boss_offset, 0, boss_center_z) * Rot(0, 90, 0) * Cylinder(boss_radius, boss_height)
solid_body = solid_body + boss

hole = Pos(boss_offset + boss_height/2 - thread_hole_depth/2, 0, boss_center_z) * Rot(0, 90, 0) * Cylinder(thread_hole_radius, thread_hole_depth)
solid_body = solid_body - hole

relief = Pos(outer_radius - relief_depth/2, 0, boss_center_z) * Box(relief_depth, relief_width, relief_height)
solid_body = solid_body - relief

part = solid_body
part.name = "tube_with_boss"
export_step(part, "output.step")