from build123d import *

plate_length = 120.0
plate_width = 80.0
plate_thickness = 6.0
boss_size = 30.0
boss_height = 4.0
boss_offset_x = 30.0
boss_offset_y = 0.0
hole_diameter = 6.0
hole_spacing = 12.0
slot_length = 40.0
slot_width = 20.0
slot_offset_x = -40.0
slot_offset_y = 0.0
chamfer_dist = 1.0
rib_width = 10.0
rib_height = 3.0
rib_offset_y = -20.0

solid = Box(plate_length, plate_width, plate_thickness)
solid = chamfer(solid.edges().filter_by(Axis.Z), chamfer_dist)

boss = Pos(boss_offset_x, boss_offset_y, plate_thickness/2 + boss_height/2) * Box(boss_size, boss_size, boss_height)
solid = solid + boss

hole_r = hole_diameter / 2
hole_h = boss_height + 0.1
for dx in [-hole_spacing/2, hole_spacing/2]:
    for dy in [-hole_spacing/2, hole_spacing/2]:
        solid = solid - Pos(boss_offset_x + dx, boss_offset_y + dy, plate_thickness/2 + boss_height/2) * Cylinder(hole_r, hole_h)

slot = Pos(slot_offset_x, slot_offset_y, 0) * Box(slot_length, slot_width, plate_thickness + 0.1)
solid = solid - slot

rib = Pos(0, rib_offset_y, -plate_thickness/2 + rib_height/2) * Box(rib_width, plate_length/2, rib_height)
solid = solid + rib

part = solid
part.name = "plate_with_boss_and_rib"
export_step(part, "output.step")