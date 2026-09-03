from build123d import *

jaw_length = 80
jaw_width = 30
jaw_thickness = 10
slot_width = 8
slot_depth = 12
slot_offset = 12
boss_diameter = 10
boss_height = 4
hole_diameter = 4
countersink_diameter = 6
countersink_angle = 82
hole_spacing = 18
hole_count = 3
chamfer_size = 0.5

solid = Box(jaw_length, jaw_width, jaw_thickness)

slot1_x = -jaw_length/2 + slot_offset
slot2_x = jaw_length/2 - slot_offset
slot1 = Pos(slot1_x, -jaw_width/2 + jaw_thickness/2, 0) * Box(slot_width, jaw_thickness, slot_depth)
slot2 = Pos(slot2_x, jaw_width/2 - jaw_thickness/2, 0) * Box(slot_width, jaw_thickness, slot_depth)
solid = solid - slot1 - slot2

boss = Pos(0, 0, jaw_thickness/2 + boss_height/2) * Cylinder(boss_diameter/2, boss_height)
solid = solid + boss

for i in range(hole_count):
    x = (i - (hole_count-1)/2) * hole_spacing
    hole = Pos(x, 0, jaw_thickness/2) * CounterSinkHole(hole_diameter/2, countersink_diameter/2, jaw_thickness, countersink_angle)
    solid = solid - hole

solid = chamfer(solid.edges().filter_by(Axis.Z), chamfer_size)

part = solid
part.name = "jaw_with_slots_boss_holes"
export_step(part, "output.step")