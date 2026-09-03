from build123d import *

plate_length = 100.0
plate_width = 70.0
plate_thickness = 4.0
cutout_width = 30.0
cutout_height = 20.0
rib_width = 20.0
rib_height = 5.0
hole_diameter = 5.5
hole_spacing = 20.0
hole_rows = 3
hole_offset_y = 15.0
chamfer_size = 0.5

base = Box(plate_length, plate_width, plate_thickness)
cutout = Box(cutout_width, cutout_height, plate_thickness)
base = base - cutout

left_rib = Pos(-plate_length/2 + rib_width/2, -plate_width/2 + rib_width/2, 0) * Box(plate_length, rib_width, rib_height)
right_rib = Pos(plate_length/2 - rib_width/2, -plate_width/2 + rib_width/2, 0) * Box(plate_length, rib_width, rib_height)

result = base + left_rib + right_rib

for i in range(hole_rows):
    x = hole_spacing * i
    y = hole_offset_y
    result = result - Pos(x, y, 0) * Cylinder(hole_diameter/2, plate_thickness + 10)

result = chamfer(result.edges().filter_by(Axis.Z), chamfer_size)

part = result
part.name = "plate_with_ribs_and_holes"
export_step(part, "output.step")