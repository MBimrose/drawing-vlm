from build123d import *

outer_diameter = 80.0
housing_length = 20.0
wall_thickness = 4.0
inner_diameter = outer_diameter - 2 * wall_thickness
pocket_width = 30.0
pocket_depth = 6.0
pocket_fillet = 2.0
mount_hole_diameter = 5.0
mount_hole_spacing = 40.0
boss_diameter = 12.0
boss_height = 8.0

outer_radius = outer_diameter / 2.0
inner_radius = inner_diameter / 2.0

with BuildPart() as p:
    with BuildSketch(Plane.XY) as sk:
        with BuildLine() as bl:
            Polyline((0, 0), (housing_length, 0), (housing_length, outer_radius), (0, outer_radius), close=True)
        make_face()
    revolve(axis=Axis.X)

solid_body = p.part
solid_body = solid_body - Rot(0, 90, 0) * Cylinder(inner_radius, housing_length)

pocket_box = Box(pocket_depth, pocket_width, pocket_depth)
pocket_box = fillet(pocket_box.edges(), pocket_fillet)

pocket_positions = [
    (inner_radius - pocket_depth / 2.0, 0, 0),
    (-(inner_radius - pocket_depth / 2.0), 0, 0),
    (0, inner_radius - pocket_depth / 2.0, 0),
    (0, -(inner_radius - pocket_depth / 2.0), 0),
]

for pos in pocket_positions:
    solid_body = solid_body - Pos(pos[0], pos[1], pos[2]) * pocket_box

for y in [-mount_hole_spacing / 2.0, mount_hole_spacing / 2.0]:
    solid_body = solid_body - Pos(housing_length / 2.0, y, 0) * Rot(0, 90, 0) * Cylinder(mount_hole_diameter / 2.0, housing_length)

solid_body = solid_body + Pos(housing_length + boss_height / 2.0, 0, 0) * Rot(0, 90, 0) * Cylinder(boss_diameter / 2.0, boss_height)

part = solid_body
part.name = "housing_with_pockets"
export_step(part, "output.step")