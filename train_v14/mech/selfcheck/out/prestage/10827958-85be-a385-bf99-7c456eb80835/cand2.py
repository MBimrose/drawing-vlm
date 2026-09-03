from build123d import *

arm_length = 80.0
arm_width = 20.0
arm_thickness = 10.0
slot_width = 6.0
slot_length = 10.0
slot_offset = 30.0
boss_diameter = 6.0
boss_height = 6.0
mount_hole_diameter = 5.0
mount_hole_spacing = 12.0
chamfer_distance = 0.5

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            l1 = Line((-arm_width/2, 0), (arm_width/2, 0))
            l2 = Line(l1@1, (arm_width/2, arm_length - arm_width/2))
            arc = ThreePointArc(l2@1, (0, arm_length), (-arm_width/2, arm_length - arm_width/2))
            l3 = Line(arc@1, (-arm_width/2, 0))
        make_face()
    extrude(amount=arm_thickness)

solid_body = p.part

slot_box = Pos(0, slot_offset, arm_thickness/2) * Box(slot_width, slot_length, arm_thickness)
solid_body = solid_body - slot_box

boss = Pos(arm_width/2 - boss_diameter/2, arm_length/2, arm_thickness + boss_height/2) * Rot(0, 90, 0) * Cylinder(boss_diameter/2, boss_height)
solid_body = solid_body + boss

for x in [-mount_hole_spacing/2, mount_hole_spacing/2]:
    hole = Pos(x, arm_width/2, arm_thickness/2) * Cylinder(mount_hole_diameter/2, arm_thickness)
    solid_body = solid_body - hole

vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = chamfer(vertical_edges, chamfer_distance)

part = solid_body
part.name = "arm_with_slot_boss_and_mounting_holes"
export_step(part, "output.step")