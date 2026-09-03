from build123d import *

plate_length = 100
plate_width = 80
plate_thickness = 5
corner_fillet = 5
central_hole_dia = 30
slot_length = 20
slot_width = 8
slot_offset_x = 30
slot_offset_y = 20
chamfer_size = 0.8
boss_extra_radius = 2
boss_height = plate_thickness / 2

solid_body = Box(plate_length, plate_width, plate_thickness)
solid_body = fillet(solid_body.edges().filter_by(Axis.Z), corner_fillet)
solid_body = solid_body - Cylinder(central_hole_dia / 2, plate_thickness)

slot_positions = [
    (slot_offset_x, slot_offset_y),
    (-slot_offset_x, slot_offset_y),
    (-slot_offset_x, -slot_offset_y),
    (slot_offset_x, -slot_offset_y),
]
for x, y in slot_positions:
    solid_body = solid_body - Pos(x, y, 0) * Box(slot_length, slot_width, plate_thickness)

solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_size)

boss_radius = central_hole_dia / 2 + boss_extra_radius
boss = Pos(0, 0, -plate_thickness / 2 - boss_height / 2) * Cylinder(boss_radius, boss_height)
solid_body = solid_body + boss

part = solid_body
part.name = "plate_with_boss"
export_step(part, "output.step")