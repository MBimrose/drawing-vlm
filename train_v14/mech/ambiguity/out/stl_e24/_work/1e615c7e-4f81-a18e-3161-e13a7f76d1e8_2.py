from build123d import *

plate_length = 80.0
plate_width = 50.0
plate_thickness = 6.0
tab_length = 30.0
tab_width = 20.0
rib_width = 30.0
rib_height = 4.0
hole_diameter = 12.0
hole_depth = plate_thickness + rib_height - 1.0
fillet_radius = 2.0
mount_hole_diameter = 5.0
mount_hole_offset = 10.0

base_plate = Pos(0, 0, plate_thickness/2) * Box(plate_length, plate_width, plate_thickness)
tab = Pos(plate_length/2 + tab_length/2, 0, plate_thickness/2) * Box(tab_length, tab_width, plate_thickness)
rib = Pos(plate_length/2 - rib_width/2, 0, plate_thickness + rib_height/2) * Box(rib_width, plate_width, rib_height)

result = base_plate + tab + rib

result = result - Pos(plate_length/3, 0, plate_thickness + rib_height - hole_depth/2) * Cylinder(hole_diameter/2, hole_depth)

for x, y in [(mount_hole_offset, mount_hole_offset), (plate_length - mount_hole_offset, mount_hole_offset),
             (mount_hole_offset, plate_width - mount_hole_offset), (plate_length - mount_hole_offset, plate_width - mount_hole_offset)]:
    result = result - Pos(x, y, plate_thickness/2) * Cylinder(mount_hole_diameter/2, plate_thickness + 1)

result = fillet(result.edges().filter_by(Axis.Z), fillet_radius)

part = result
part.name = "plate_with_tab_rib_and_holes"
export_step(part, "output.step")