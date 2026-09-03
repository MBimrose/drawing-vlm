from build123d import *

plate_length = 80.0
plate_width = 40.0
plate_thickness = 5.0
slot_width = 20.0
slot_length = 30.0
hole_diameter = 10.0
hole_offset_from_end = 10.0
chamfer_distance = 1.0
rib_width = 5.0
rib_height = 3.0
rib_spacing = 15.0

result = Box(plate_length, plate_width, plate_thickness)

with BuildPart() as slot_bp:
    with BuildSketch() as slot_sk:
        SlotOverall(slot_length, slot_width)
    extrude(amount=plate_thickness * 2)
slot_solid = Pos(0, 0, -plate_thickness / 2) * slot_bp.part
result = result - slot_solid

for x in [-plate_length / 2 + hole_offset_from_end, plate_length / 2 - hole_offset_from_end]:
    result = result - Pos(x, 0, 0) * Cylinder(hole_diameter / 2, plate_thickness * 2)

result = chamfer(result.edges().filter_by(Axis.Z), chamfer_distance)

for x in [-plate_length / 2 + rib_spacing / 2, plate_length / 2 - rib_spacing / 2]:
    rib = Pos(x, 0, -plate_thickness / 2 + rib_height / 2) * Box(rib_width, plate_thickness, rib_height)
    result = result + rib

part = result
part.name = "plate_with_slot_holes_and_ribs"
export_step(part, "output.step")