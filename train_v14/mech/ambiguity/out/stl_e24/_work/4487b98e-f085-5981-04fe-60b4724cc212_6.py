from build123d import *

plate_length = 100
plate_width = 80
plate_thickness = 5
corner_fillet_radius = 5
central_hole_diameter = 30
slot_length = 20
slot_width = 8
slot_offset = 15
rib_height = 2
rib_thickness = 2
chamfer_distance = 0.8

with BuildPart() as p:
    with BuildSketch() as s:
        Rectangle(plate_length, plate_width)
    extrude(amount=plate_thickness)

solid_body = p.part
solid_body = fillet(solid_body.edges().filter_by(Axis.Z), corner_fillet_radius)

solid_body = solid_body - Pos(0, 0, plate_thickness/2) * Cylinder(central_hole_diameter/2, plate_thickness + 1)

slot_positions = [
    (plate_length/2 - slot_offset - slot_length/2, plate_width/2 - slot_offset - slot_width/2),
    (-plate_length/2 + slot_offset + slot_length/2, plate_width/2 - slot_offset - slot_width/2),
    (-plate_length/2 + slot_offset + slot_length/2, -plate_width/2 + slot_offset + slot_width/2),
    (plate_length/2 - slot_offset - slot_length/2, -plate_width/2 + slot_offset + slot_width/2),
]
for x, y in slot_positions:
    solid_body = solid_body - Pos(x, y, plate_thickness/2) * Box(slot_length, slot_width, plate_thickness + 1)

rib_radius = central_hole_diameter/2 + rib_thickness
solid_body = solid_body + Pos(0, 0, -rib_height/2) * Cylinder(rib_radius, rib_height)

solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_distance)

part = solid_body
part.name = "plate_with_slots_and_rib"
export_step(part, "output.step")