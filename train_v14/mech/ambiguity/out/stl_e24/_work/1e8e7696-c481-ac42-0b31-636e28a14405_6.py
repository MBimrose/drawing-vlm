from build123d import *

plate_length = 100.0
plate_width = 80.0
plate_thickness = 6.0
rib_width = 30.0
rib_height = 30.0
rib_thickness = 4.0
rib_offset_x = 15.0
slot_length = 40.0
slot_width = 20.0
slot_offset_x = -plate_length/2 + 10.0
hole_diameter = 6.0
hole_spacing = 12.0
hole_rows = 2
hole_cols = 2
chamfer_size = 1.0

base = Box(plate_length, plate_width, plate_thickness)
base = chamfer(base.edges().filter_by(Axis.Z), chamfer_size)

rib = Pos(plate_length/2 - rib_offset_x, 0, plate_thickness/2 + rib_thickness/2) * Box(rib_width, rib_height, rib_thickness)
base = base + rib

slot = Pos(slot_offset_x, 0, 0) * Box(slot_length, slot_width, plate_thickness)
base = base - slot

hole_r = hole_diameter / 2
hole_h = plate_thickness + rib_thickness + 2
for i in range(hole_cols):
    for j in range(hole_rows):
        x = plate_length/2 - rib_offset_x + (i - (hole_cols-1)/2) * hole_spacing
        y = (j - (hole_rows-1)/2) * hole_spacing
        base = base - Pos(x, y, plate_thickness/2 + rib_thickness/2) * Cylinder(hole_r, hole_h)

part = base
part.name = "plate_with_rib_slot_holes"
export_step(part, "output.step")