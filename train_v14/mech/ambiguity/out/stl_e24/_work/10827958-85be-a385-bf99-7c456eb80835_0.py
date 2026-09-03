from build123d import *

arm_length = 80.0
arm_width = 20.0
arm_thickness = 10.0
fillet_radius = 3.0
slot_width = 6.0
slot_length = 12.0
slot_offset = 10.0
hole_diameter = 5.0
hole_spacing = 12.0
hole_offset = 10.0
boss_radius = 3.0
boss_length = 12.0
boss_offset = 30.0
chamfer_distance = 0.5

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            l1 = Line((0, 0), (arm_width, 0))
            l2 = Line(l1 @ 1, (arm_width, arm_length - fillet_radius))
            a1 = ThreePointArc(l2 @ 1, (arm_width / 2, arm_length), (0, arm_length - fillet_radius))
            l3 = Line(a1 @ 1, (0, 0))
        make_face()
    extrude(amount=arm_thickness)

solid_body = p.part

slot_center_x = slot_offset + slot_width / 2
slot_center_y = arm_length / 2 - slot_length / 2
slot_cut = Pos(slot_center_x, slot_center_y, arm_thickness / 2) * Box(slot_width, slot_length, arm_thickness)
solid_body = solid_body - slot_cut

hole_center_x = hole_offset + hole_spacing / 2
hole_center_y = arm_length / 2 - hole_spacing / 2
for dx in [-hole_spacing / 2, hole_spacing / 2]:
    for dy in [-hole_spacing / 2, hole_spacing / 2]:
        hole_cut = Pos(hole_center_x + dx, hole_center_y + dy, arm_thickness / 2) * Cylinder(hole_diameter / 2, arm_thickness)
        solid_body = solid_body - hole_cut

boss_center_x = boss_offset + boss_length / 2
boss_center_y = arm_length / 2 - boss_length / 2
boss = Pos(boss_center_x, boss_center_y, arm_thickness + boss_length / 2) * Rot(0, 90, 0) * Cylinder(boss_radius, boss_length)
solid_body = solid_body + boss

vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = chamfer(vertical_edges, chamfer_distance)

part = solid_body
part.name = "arm_with_slot_holes_boss"
export_step(part, "output.step")