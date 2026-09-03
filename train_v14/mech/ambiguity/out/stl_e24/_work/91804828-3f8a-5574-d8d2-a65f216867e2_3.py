from build123d import *

plate_width = 80.0
plate_height = 60.0
plate_thickness = 4.0
flange_height = 10.0
cutout_width = 30.0
cutout_height = 20.0
slot_length = 50.0
slot_width = 5.0
hole_diameter = 5.5
hole_spacing = 20.0
hole_rows = 3
hole_cols = 4
chamfer_size = 0.5

base = Box(plate_width, plate_height, plate_thickness)
flange = Pos(0, -(plate_height/2 + flange_height/2), 0) * Box(plate_width, flange_height, plate_thickness)
result = base + flange

result = result - Box(cutout_width, cutout_height, plate_thickness)

with BuildPart() as slot_bp:
    with BuildSketch() as slot_sk:
        SlotOverall(slot_length, slot_width)
    extrude(amount=plate_thickness)
slot_solid = Pos(0, -(plate_height/2 + flange_height/2), -plate_thickness/2) * slot_bp.part
result = result - slot_solid

for i in range(hole_cols):
    for j in range(hole_rows):
        x = (i - (hole_cols-1)/2) * hole_spacing
        y = (j - (hole_rows-1)/2) * hole_spacing
        result = result - Pos(x, y, 0) * Cylinder(hole_diameter/2, plate_thickness)

result = chamfer(result.edges().filter_by(Axis.Z), chamfer_size)

part = result
part.name = "plate_with_flange_and_holes"
export_step(part, "output.step")