from build123d import *

arm_length = 80.0
base_width = 12.0
tip_width = 6.0
thickness = 8.0
boss_diameter = 12.0
boss_height = 4.0
slot_width = 4.0
slot_length = 20.0
slot_offset = 30.0
hole_diameter = 3.0
hole_spacing = 20.0
hole_count = 3
chamfer_size = 1.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0, -base_width/2), (arm_length*0.6, -base_width/2),
                     (arm_length, -tip_width/2), (arm_length, tip_width/2),
                     (arm_length*0.6, base_width/2), (0, base_width/2), close=True)
        make_face()
    extrude(amount=thickness)

solid_body = p.part

slot_center_x = arm_length/2 + slot_offset
slot_cut = Pos(slot_center_x, base_width/2 - thickness/4, thickness/2) * Box(slot_length, thickness/2, slot_width)
solid_body = solid_body - slot_cut

boss = Pos(arm_length, 0, 0) * Rot(0, 90, 0) * Cylinder(boss_diameter/2, boss_diameter)
solid_body = solid_body + boss

for i in range(hole_count):
    hx = arm_length/2 + (i - (hole_count-1)/2) * hole_spacing
    hole = Pos(hx, 0, thickness/2) * Cylinder(hole_diameter/2, thickness)
    solid_body = solid_body - hole

tip_edges = solid_body.edges().filter_by(Axis.Z).sort_by(Axis.X)[-2:]
solid_body = chamfer(tip_edges, chamfer_size)

part = solid_body
part.name = "tapered_arm_with_boss"
export_step(part, "output.step")