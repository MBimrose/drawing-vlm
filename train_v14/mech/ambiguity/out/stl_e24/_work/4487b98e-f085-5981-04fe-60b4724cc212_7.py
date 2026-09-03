from build123d import *

plate_width = 100
plate_height = 80
plate_thickness = 5
corner_fillet_radius = 5
central_hole_diameter = 30
slot_width = 20
slot_height = 8
slot_offset = 30
chamfer_distance = 0.8
boss_extra_radius = 2
boss_height = 3

with BuildPart() as p:
    with BuildSketch() as s:
        Rectangle(plate_width, plate_height)
    extrude(amount=plate_thickness)

solid_body = p.part
solid_body = fillet(solid_body.edges().filter_by(Axis.Z), corner_fillet_radius)

solid_body = solid_body - Cylinder(central_hole_diameter/2, plate_thickness * 2)

slot_positions = [
    (slot_offset, slot_offset),
    (-slot_offset, slot_offset),
    (-slot_offset, -slot_offset),
    (slot_offset, -slot_offset)
]
for x, y in slot_positions:
    solid_body = solid_body - Pos(x, y, 0) * Box(slot_width, slot_height, plate_thickness * 2)

solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_distance)

boss_radius = central_hole_diameter/2 + boss_extra_radius
solid_body = solid_body + Pos(0, 0, -boss_height/2) * Cylinder(boss_radius, boss_height)

part = solid_body
part.name = "plate_with_slots_and_boss"
export_step(part, "output.step")