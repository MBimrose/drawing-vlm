from build123d import *

outer_radius = 30.0
inner_radius = 12.0
collar_length = 20.0
fillet_radius = 5.0
chamfer_distance = 2.0
keyway_width = 6.0
keyway_depth = 4.0
boss_radius = 4.0
boss_height = 8.0
mount_hole_diameter = 4.0
mount_hole_offset = 18.0

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            l1 = Line((outer_radius, 0), (outer_radius, collar_length - fillet_radius))
            l2 = ThreePointArc(l1 @ 1, (outer_radius - fillet_radius, collar_length), (inner_radius, collar_length))
            l3 = Line(l2 @ 1, (inner_radius, 0))
            l4 = Line(l3 @ 1, (outer_radius, 0))
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part

bottom_face = solid_body.faces().sort_by(Axis.Z)[0]
solid_body = chamfer(bottom_face.edges(), chamfer_distance)

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = fillet(top_face.edges(), fillet_radius)

keyway_box = Pos(inner_radius - keyway_depth / 2, 0, 0) * Box(keyway_depth, collar_length, keyway_width)
solid_body = solid_body - keyway_box

boss_cyl = Pos(outer_radius - boss_radius - 2, 0, 0) * Rot(0, 90, 0) * Cylinder(boss_radius, boss_height)
solid_body = solid_body + boss_cyl

for x in [-mount_hole_offset, mount_hole_offset]:
    hole_cyl = Pos(x, 0, collar_length / 2) * Cylinder(mount_hole_diameter / 2, collar_length + 10)
    solid_body = solid_body - hole_cyl

part = solid_body
part.name = "collar_with_keyway_and_boss"
export_step(part, "output.step")