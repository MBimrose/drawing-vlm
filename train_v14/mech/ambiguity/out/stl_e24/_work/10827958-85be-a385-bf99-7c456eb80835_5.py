from build123d import *

arm_length = 80.0
arm_width = 20.0
arm_thickness = 10.0
fillet_radius = 3.0
chamfer_distance = 0.5
slot_width = 6.0
slot_length = 30.0
slot_offset = 30.0
hole_diameter = 5.0
hole_spacing = 12.0
hole_offset = 10.0
boss_diameter = 6.0
boss_height = 5.0
boss_offset = 40.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            l1 = Line((0, 0), (arm_width, 0))
            l2 = Line(l1 @ 1, (arm_width, arm_length - fillet_radius))
            arc = ThreePointArc(l2 @ 1, (arm_width / 2, arm_length), (0, arm_length - fillet_radius))
            l3 = Line(arc @ 1, (0, 0))
        make_face()
    extrude(amount=arm_thickness)

solid_body = p.part

slot_box = Pos(arm_width / 2, slot_offset, arm_thickness / 2) * Box(slot_width, arm_thickness, slot_length)
solid_body = solid_body - slot_box

for i in range(2):
    hx = arm_width / 2 + (i - 0.5) * hole_spacing
    hy = hole_offset
    hole = Pos(hx, hy, arm_thickness / 2) * Cylinder(hole_diameter / 2, arm_thickness)
    solid_body = solid_body - hole

boss = Pos(arm_width / 2, boss_offset, arm_thickness + boss_height / 2) * Rot(0, 90, 0) * Cylinder(boss_diameter / 2, boss_height)
solid_body = solid_body + boss

vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = chamfer(vertical_edges, chamfer_distance)

part = solid_body
part.name = "arm_with_slot_holes_boss"
export_step(part, "output.step")