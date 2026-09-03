from build123d import *

lever_length = 80.0
lever_width = 20.0
lever_thickness = 10.0
tip_radius = 5.0
boss_diameter = 6.0
boss_height = 12.0
boss_offset = 30.0
slot_width = 6.0
slot_length = 10.0
slot_offset = 15.0
mount_hole_dia = 5.0
mount_hole_spacing = 12.0
mount_hole_offset = 5.0
chamfer_size = 0.5

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            l1 = Line((0, 0), (lever_width, 0))
            l2 = Line(l1 @ 1, (lever_width, lever_length - tip_radius))
            arc = ThreePointArc(l2 @ 1, (lever_width / 2, lever_length), (0, lever_length - tip_radius))
            l3 = Line(arc @ 1, (0, 0))
        make_face()
    extrude(amount=lever_thickness)

solid_body = p.part
solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_size)

slot_cut = Pos(lever_width / 2, slot_offset, lever_thickness / 2) * Box(slot_width, slot_length, lever_thickness)
solid_body = solid_body - slot_cut

boss = Pos(lever_width / 2, boss_offset, lever_thickness + boss_height / 2) * Rot(0, 90, 0) * Cylinder(boss_diameter / 2, boss_height)
solid_body = solid_body + boss

for x, y in [(lever_width / 2 - mount_hole_spacing / 2, mount_hole_offset),
             (lever_width / 2 + mount_hole_spacing / 2, mount_hole_offset)]:
    hole = Pos(x, y, lever_thickness / 2) * Cylinder(mount_hole_dia / 2, lever_thickness + 2)
    solid_body = solid_body - hole

part = solid_body
part.name = "lever"
export_step(part, "output.step")