from build123d import *

plate_length = 80.0
plate_width = 50.0
plate_thickness = 8.0
rib_height = 3.0
rib_thickness = 2.0
slot_width = 6.0
slot_length = 10.0
slot_offset = 5.0
hole_diameter = 4.0
countersink_diameter = 8.0
countersink_angle = 90.0
hole_offset = 10.0
chamfer_size = 1.0

with BuildPart() as p:
    with BuildSketch() as s:
        Rectangle(plate_length, plate_width)
    extrude(amount=plate_thickness)
base = p.part
base = chamfer(base.edges().filter_by(Axis.Z), chamfer_size)

with BuildPart() as p2:
    with BuildSketch() as s2:
        Rectangle(plate_length, plate_width)
    extrude(amount=rib_height)
rib = p2.part
rib = rib - Pos(0, 0, rib_height/2) * Box(plate_length - 2*rib_thickness, plate_width - 2*rib_thickness, rib_height)
rib = Pos(0, 0, plate_thickness - 0.5) * rib

result = base + rib

slot = Pos(plate_length/2 - slot_offset - slot_width/2, plate_width/2 - slot_offset - slot_length/2, 0) * Box(slot_width, slot_length, plate_thickness)
result = result - slot

hole1 = Pos(hole_offset, hole_offset, plate_thickness) * CounterSinkHole(hole_diameter/2, countersink_diameter/2, plate_thickness, countersink_angle)
hole2 = Pos(plate_length - hole_offset, plate_width - hole_offset, plate_thickness) * CounterSinkHole(hole_diameter/2, countersink_diameter/2, plate_thickness, countersink_angle)
result = result - hole1 - hole2

part = result
part.name = "plate_with_rib_slot_and_holes"
export_step(part, "output.step")