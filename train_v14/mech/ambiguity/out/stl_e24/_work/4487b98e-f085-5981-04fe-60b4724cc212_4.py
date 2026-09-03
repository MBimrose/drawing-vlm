from build123d import *

plate_length = 100.0
plate_width = 80.0
plate_thickness = 5.0
corner_fillet_radius = 5.0
central_hole_diameter = 30.0
slot_length = 20.0
slot_width = 8.0
slot_offset = 30.0
edge_chamfer = 0.8
boss_extra_radius = 2.0
boss_height = plate_thickness / 2.0

solid_body = Box(plate_length, plate_width, plate_thickness)
solid_body = fillet(solid_body.edges().filter_by(Axis.Z), corner_fillet_radius)
solid_body = solid_body - Cylinder(central_hole_diameter / 2, plate_thickness)

slot_positions = [
    (slot_offset, slot_offset),
    (-slot_offset, slot_offset),
    (-slot_offset, -slot_offset),
    (slot_offset, -slot_offset),
]
for x, y in slot_positions:
    solid_body = solid_body - Pos(x, y, 0) * Box(slot_length, slot_width, plate_thickness)

solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), edge_chamfer)

boss_radius = central_hole_diameter / 2 + boss_extra_radius
solid_body = solid_body + Pos(0, 0, -plate_thickness / 2 - boss_height / 2) * Cylinder(boss_radius, boss_height)

part = solid_body
part.name = "plate_with_slots_and_boss"
export_step(part, "output.step")