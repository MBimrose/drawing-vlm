from build123d import *

outer_radius = 30.0
inner_radius = 12.0
collar_length = 20.0
shoulder_radius = 4.0
relief_groove_depth = 2.0
relief_groove_width = 4.0
chamfer_size = 2.0
mount_hole_diameter = 4.0
mount_hole_offset = 18.0
boss_radius = 4.0
boss_height = 6.0

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            l1 = Line((inner_radius, 0), (outer_radius, 0))
            l2 = Line(l1 @ 1, (outer_radius, collar_length - shoulder_radius))
            arc = ThreePointArc(l2 @ 1, (outer_radius - shoulder_radius, collar_length), (inner_radius, collar_length))
            l3 = Line(arc @ 1, (inner_radius, 0))
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part

bottom_face = solid_body.faces().sort_by(Axis.Z)[0]
solid_body = chamfer(bottom_face.edges(), chamfer_size)

solid_body = solid_body - Pos(0, 0, collar_length/2) * Cylinder(inner_radius - relief_groove_depth, relief_groove_width)
solid_body = solid_body - Pos(0, 0, collar_length/2) * Cylinder(outer_radius - relief_groove_depth, relief_groove_width)

for x in [-mount_hole_offset, mount_hole_offset]:
    solid_body = solid_body - Pos(x, 0, collar_length/2) * Cylinder(mount_hole_diameter/2, collar_length + 10)

solid_body = solid_body + Pos(inner_radius, 0, 0) * Rot(0, 90, 0) * Cylinder(boss_radius, boss_height)

part = solid_body
part.name = "collar_with_boss"
export_step(part, "output.step")