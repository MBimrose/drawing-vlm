from build123d import *

plate_width = 80.0
plate_height = 50.0
plate_thickness = 6.0
central_hole_diameter = 30.0
clearance_hole_diameter = 5.0
clearance_hole_spacing_x = 12.0
clearance_hole_spacing_y = 12.0
clearance_hole_rows = 2
clearance_hole_cols = 5
mount_hole_diameter = 6.0
mount_hole_offset_x = 30.0
rib_thickness = 4.0
rib_height = 25.0
chamfer_distance = 0.5

result = Box(plate_width, plate_thickness, plate_height)
result = result - Rot(90, 0, 0) * Cylinder(central_hole_diameter/2, plate_thickness)

for i in range(clearance_hole_cols):
    for j in range(clearance_hole_rows):
        x = (i - (clearance_hole_cols-1)/2) * clearance_hole_spacing_x
        z = (j - (clearance_hole_rows-1)/2) * clearance_hole_spacing_y
        result = result - Pos(x, 0, z) * Rot(90, 0, 0) * Cylinder(clearance_hole_diameter/2, plate_thickness)

for x in [-mount_hole_offset_x, mount_hole_offset_x]:
    result = result - Pos(x, 0, 0) * Rot(90, 0, 0) * Cylinder(mount_hole_diameter/2, plate_thickness)

rib = Box(rib_thickness, rib_thickness, rib_height)
result = result + Pos(plate_width/2 + rib_thickness/2, 0, 0) * rib
result = result + Pos(-plate_width/2 - rib_thickness/2, 0, 0) * rib

result = chamfer(result.edges(), chamfer_distance)

part = result
part.name = "plate_with_ribs_and_holes"
export_step(part, "output.step")