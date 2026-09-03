from build123d import *
import math

plate_length = 80.0
plate_width = 60.0
plate_thickness = 4.0
slot_length = 30.0
slot_width = 8.0
slot_spacing = 30.0
hole_diameter = 4.0
hole_pattern_radius = 20.0
hole_count = 6
chamfer_size = 0.5
fillet_radius = 0.4
rib_height = 2.0
rib_margin = 5.0

with BuildPart() as p:
    with BuildSketch() as s:
        Rectangle(plate_length, plate_width)
    extrude(amount=plate_thickness)

solid_body = p.part
solid_body = chamfer(solid_body.edges(), chamfer_size)

with BuildPart() as slot_p:
    with BuildSketch() as slot_s:
        SlotOverall(slot_length, slot_width)
    extrude(amount=plate_thickness)
slot_solid = slot_p.part

solid_body = solid_body - Pos(0, slot_spacing/2, 0) * slot_solid
solid_body = solid_body - Pos(0, -slot_spacing/2, 0) * slot_solid

for i in range(hole_count):
    angle = math.radians(i * 360.0 / hole_count)
    px = hole_pattern_radius * math.cos(angle)
    py = hole_pattern_radius * math.sin(angle)
    solid_body = solid_body - Pos(px, py, 0) * Cylinder(hole_diameter/2, plate_thickness * 2)

rib = Pos(0, 0, plate_thickness/2 + rib_height/2) * Box(plate_length - 2*rib_margin, plate_width - 2*rib_margin, rib_height)
solid_body = solid_body + rib

solid_body = fillet(solid_body.edges(), fillet_radius)

part = solid_body
part.name = "plate_with_slots_holes_and_rib"
export_step(part, "output.step")