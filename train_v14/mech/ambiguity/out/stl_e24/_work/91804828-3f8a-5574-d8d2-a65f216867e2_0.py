from build123d import *

plate_width = 100.0
plate_height = 70.0
plate_thickness = 4.0
cutout_width = 30.0
cutout_height = 20.0
slot_length = 60.0
slot_width = 5.0
slot_offset_x = -plate_width/2 + 10.0
slot_offset_y = -plate_height/2 + 15.0
hole_diameter = 5.5
hole_spacing_x = 20.0
hole_spacing_y = 20.0
hole_rows = 2
hole_cols = 3
hole_array_offset_x = 30.0
hole_array_offset_y = 20.0
chamfer_size = 0.5

solid_body = Box(plate_width, plate_height, plate_thickness)
solid_body = solid_body - Box(cutout_width, cutout_height, plate_thickness)

with BuildPart() as slot_bp:
    with BuildSketch() as slot_sk:
        SlotOverall(slot_length, slot_width)
    extrude(amount=plate_thickness)
slot_solid = Pos(slot_offset_x, slot_offset_y, -plate_thickness/2) * slot_bp.part
solid_body = solid_body - slot_solid

for i in range(hole_cols):
    for j in range(hole_rows):
        x = hole_array_offset_x + (i - (hole_cols-1)/2) * hole_spacing_x
        y = hole_array_offset_y + (j - (hole_rows-1)/2) * hole_spacing_y
        solid_body = solid_body - Pos(x, y, 0) * Cylinder(hole_diameter/2, plate_thickness)

solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_size)

part = solid_body
part.name = "plate_with_cutouts"
export_step(part, "output.step")