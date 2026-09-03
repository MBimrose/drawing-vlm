from build123d import *

plate_width = 80.0
plate_height = 60.0
plate_thickness = 4.0
flange_height = 10.0
pocket_width = 30.0
pocket_height = 20.0
slot_length = 50.0
slot_width = 5.0
hole_diameter = 5.5
hole_spacing_x = 20.0
hole_spacing_y = 20.0
hole_rows = 2
hole_cols = 3
chamfer_size = 0.5

base = Box(plate_width, plate_height, plate_thickness)
flange = Pos(0, -(plate_height/2 + flange_height/2), 0) * Box(plate_width, flange_height, plate_thickness)
result = base + flange

pocket = Box(pocket_width, pocket_height, plate_thickness)
result = result - pocket

with BuildPart() as slot_bp:
    with BuildSketch() as slot_sk:
        SlotOverall(slot_length, slot_width)
    extrude(amount=plate_thickness)
slot_solid = Pos(0, -(plate_height/2 + flange_height/2), -plate_thickness/2) * slot_bp.part
result = result - slot_solid

for row in range(hole_rows):
    for col in range(hole_cols):
        x = col * hole_spacing_x
        y = plate_height/2 - (row + 1) * hole_spacing_y
        result = result - Pos(x, y, 0) * Cylinder(hole_diameter/2, plate_thickness)

result = chamfer(result.edges().filter_by(Axis.Z), chamfer_size)

part = result
part.name = "plate_with_flange_pocket_slot_holes"
export_step(part, "output.step")