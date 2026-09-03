from build123d import *

arm_length = 80.0
arm_width = 30.0
arm_thickness = 10.0
notch_width = 10.0
notch_depth = 5.0
slot_width = 8.0
slot_length = 12.0
slot_offset = 15.0
boss_diameter = 10.0
boss_height = 4.0
hole_diameter = 4.0
countersink_diameter = 6.0
countersink_angle = 82.0
hole_spacing = 18.0
chamfer_size = 0.5

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline(
                (-arm_length/2, -arm_width/2),
                (arm_length/2, -arm_width/2),
                (arm_length/2, arm_width/2 - notch_depth),
                (arm_length/2 - notch_width, arm_width/2 - notch_depth),
                (arm_length/2 - notch_width, arm_width/2),
                (-arm_length/2, arm_width/2),
                close=True
            )
        make_face()
    extrude(amount=arm_thickness)

solid_body = p.part

slot_center_x = -arm_length/2 + slot_offset
slot_cut = Pos(slot_center_x, -arm_width/2 + arm_thickness/2, arm_thickness/2) * Box(slot_width, arm_thickness, slot_length)
solid_body = solid_body - slot_cut

boss = Pos(0, 0, arm_thickness + boss_height/2) * Cylinder(boss_diameter/2, boss_height)
solid_body = solid_body + boss

for i in range(3):
    x = (i - 1) * hole_spacing
    csk = Pos(x, 0, arm_thickness) * CounterSinkHole(hole_diameter/2, countersink_diameter/2, arm_thickness, countersink_angle)
    solid_body = solid_body - csk

solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_size)

part = solid_body
part.name = "arm_plate"
export_step(part, "output.step")