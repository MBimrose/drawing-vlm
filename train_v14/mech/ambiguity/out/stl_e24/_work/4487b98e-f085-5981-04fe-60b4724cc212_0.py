from build123d import *

plate_length = 100.0
plate_width = 80.0
plate_thickness = 5.0
corner_fillet_radius = 5.0
central_hole_diameter = 30.0
slot_length = 20.0
slot_width = 8.0
slot_offset_x = 30.0
slot_offset_y = 20.0
chamfer_distance = 0.8
boss_extra_height = 2.5
boss_clearance = 2.0

with BuildPart() as p:
    with BuildSketch() as s:
        Rectangle(plate_length, plate_width)
    extrude(amount=plate_thickness)

solid_body = p.part
solid_body = fillet(solid_body.edges().filter_by(Axis.Z), corner_fillet_radius)

solid_body = solid_body - Cylinder(central_hole_diameter / 2, plate_thickness * 2)

slot_positions = [
    (slot_offset_x, slot_offset_y),
    (-slot_offset_x, slot_offset_y),
    (slot_offset_x, -slot_offset_y),
    (-slot_offset_x, -slot_offset_y),
]
for x, y in slot_positions:
    solid_body = solid_body - Pos(x, y, 0) * Box(slot_length, slot_width, plate_thickness * 2)

boss_diameter = central_hole_diameter + boss_clearance
solid_body = solid_body + Pos(0, 0, -boss_extra_height / 2) * Cylinder(boss_diameter / 2, boss_extra_height)

solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_distance)

part = solid_body
part.name = "plate_with_boss_and_slots"
export_step(part, "output.step")