from build123d import *

outer_radius = 30.0
wall_thickness = 3.0
inner_radius = outer_radius - wall_thickness
housing_length = 80.0
split_gap = 2.0
boss_radius = 6.0
boss_height = 8.0
boss_offset = 20.0
boss_hole_diameter = 6.0
mount_hole_diameter = 4.0
mount_hole_spacing = 40.0

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            l1 = Line((inner_radius, -housing_length/2), (outer_radius, -housing_length/2))
            l2 = Line(l1@1, (outer_radius, housing_length/2))
            l3 = Line(l2@1, (inner_radius, housing_length/2))
            l4 = Line(l3@1, (inner_radius, -housing_length/2))
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part

split_cut = Pos(outer_radius - split_gap/2, 0, 0) * Box(split_gap, housing_length, wall_thickness + 0.2)
solid_body = solid_body - split_cut

boss = Pos(boss_offset, -boss_height/2, 0) * Rot(90, 0, 0) * Cylinder(boss_radius, boss_height)
solid_body = solid_body + boss

boss_hole = Pos(boss_offset, -boss_height/2, 0) * Rot(90, 0, 0) * Cylinder(boss_hole_diameter/2, boss_height + 2)
solid_body = solid_body - boss_hole

for x in [-mount_hole_spacing/2, mount_hole_spacing/2]:
    hole = Pos(x, 0, 0) * Rot(90, 0, 0) * Cylinder(mount_hole_diameter/2, wall_thickness + 2)
    solid_body = solid_body - hole

part = solid_body
part.name = "split_housing_with_boss"
export_step(part, "output.step")