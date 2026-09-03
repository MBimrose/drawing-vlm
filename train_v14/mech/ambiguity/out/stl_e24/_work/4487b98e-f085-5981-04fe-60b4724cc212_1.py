from build123d import *

plate_length = 100.0
plate_width = 80.0
plate_thickness = 5.0
corner_radius = 5.0
central_hole_diameter = 30.0
slot_length = 20.0
slot_width = 8.0
slot_offset = 15.0
chamfer_distance = 0.8
rib_height = 2.0
rib_width = 6.0
rib_spacing = 20.0
boss_extra_radius = 2.0
boss_height = plate_thickness / 2.0

with BuildPart() as p:
    with BuildSketch() as s:
        Rectangle(plate_length, plate_width)
    extrude(amount=plate_thickness)

solid_body = p.part
solid_body = fillet(solid_body.edges().filter_by(Axis.Z), corner_radius)

solid_body = solid_body - Pos(0, 0, plate_thickness/2) * Cylinder(central_hole_diameter/2, plate_thickness)

slot_positions = [
    (-plate_length/2 + slot_offset + slot_length/2, -plate_width/2 + slot_offset + slot_width/2),
    ( plate_length/2 - slot_offset - slot_length/2, -plate_width/2 + slot_offset + slot_width/2),
    (-plate_length/2 + slot_offset + slot_length/2,  plate_width/2 - slot_offset - slot_width/2),
    ( plate_length/2 - slot_offset - slot_length/2,  plate_width/2 - slot_offset - slot_width/2),
]
for x, y in slot_positions:
    solid_body = solid_body - Pos(x, y, plate_thickness/2) * Box(slot_length, slot_width, plate_thickness)

solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_distance)

num_ribs = int((plate_length - 2*slot_offset) // rib_spacing) + 1
for i in range(num_ribs):
    x = -plate_length/2 + slot_offset + i * rib_spacing
    solid_body = solid_body + Pos(x, 0, plate_thickness/4) * Box(rib_width, rib_height, plate_thickness/2)

solid_body = solid_body + Pos(0, 0, -boss_height/2) * Cylinder(central_hole_diameter/2 + boss_extra_radius, boss_height)

part = solid_body
part.name = "plate_with_slots_ribs_boss"
export_step(part, "output.step")