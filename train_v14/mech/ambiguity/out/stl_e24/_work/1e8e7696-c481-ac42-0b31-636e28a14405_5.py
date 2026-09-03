from build123d import *

plate_length = 120.0
plate_width = 80.0
plate_thickness = 6.0
rib_width = 30.0
rib_height = 4.0
rib_offset = 15.0
hole_diameter = 6.0
hole_spacing = 12.0
chamfer_size = 1.0
cutout_width = 20.0
cutout_length = 40.0
cutout_offset = 10.0

result = Box(plate_length, plate_width, plate_thickness)
result = chamfer(result.edges().filter_by(Axis.Z), chamfer_size)

cutout_x = -plate_length/2 + cutout_offset + cutout_length/2
result = result - Pos(cutout_x, 0, 0) * Box(cutout_length, cutout_width, plate_thickness)

rib_x = plate_length/2 - rib_offset - rib_width/2
result = result + Pos(rib_x, 0, plate_thickness/2 + rib_height/2) * Box(rib_width, rib_width, rib_height)

hole_r = hole_diameter / 2
hole_h = plate_thickness + rib_height + 2
for dx, dy in [(-hole_spacing/2, -hole_spacing/2), (hole_spacing/2, -hole_spacing/2),
               (-hole_spacing/2, hole_spacing/2), (hole_spacing/2, hole_spacing/2)]:
    result = result - Pos(rib_x + dx, dy, plate_thickness/2 + rib_height/2) * Cylinder(hole_r, hole_h)

part = result
part.name = "plate_with_rib_and_holes"
export_step(part, "output.step")