from build123d import *

arm_length = 80.0
arm_width_start = 12.0
arm_width_end = 6.0
arm_thickness = 6.0
boss_diameter = 12.0
boss_height = 20.0
chamfer_size = 1.0
hole_diameter = 4.0
hole_spacing = 30.0
rib_thickness = 3.0
rib_height = 4.0
rib_length = arm_length - 10.0
slot_width = 4.0
slot_length = 15.0
slot_offset = 10.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0, -arm_width_start/2), (arm_length, -arm_width_end/2),
                     (arm_length, arm_width_end/2), (0, arm_width_start/2), close=True)
        make_face()
    extrude(amount=arm_thickness)

solid_body = p.part

slot_cut = Pos(arm_length/2, arm_width_start/2 - arm_thickness/2, arm_thickness/2) * Box(slot_length, arm_thickness, slot_width)
solid_body = solid_body - slot_cut

boss = Pos(arm_length, 0, 0) * Rot(0, 90, 0) * Cylinder(boss_diameter/2, boss_height)
boss_edges = boss.edges().sort_by(Axis.X)[:1]
boss = chamfer(boss_edges, chamfer_size)
solid_body = solid_body + boss

rib = Pos(rib_length/2, 0, rib_thickness/2) * Box(rib_length, rib_height, rib_thickness)
solid_body = solid_body + rib

for x in [arm_length/2 - hole_spacing/2, arm_length/2 + hole_spacing/2]:
    solid_body = solid_body - Pos(x, 0, 0) * Cylinder(hole_diameter/2, arm_thickness + 10)

part = solid_body
part.name = "tapered_arm_with_boss"
export_step(part, "output.step")