from build123d import *

plate_length = 80.0
plate_width = 60.0
plate_thickness = 8.0
corner_fillet_radius = 2.0
bearing_radius = 12.0
bearing_depth = 4.0
bearing_offset_x = 20.0
bearing_offset_y = 0.0
notch_width = 30.0
notch_height = 10.0
notch_depth = 3.0
rib_thickness = 4.0
rib_height = 20.0

result = Box(plate_length, plate_width, plate_thickness)
result = fillet(result.edges().filter_by(Axis.Z), corner_fillet_radius)

notch = Pos(0, plate_width/2 - notch_height/2, plate_thickness - notch_depth/2) * Box(notch_width, notch_height, notch_depth)
result = result - notch

bearing = Pos(bearing_offset_x, bearing_offset_y, plate_thickness/2 - bearing_depth/2) * Cylinder(bearing_radius, bearing_depth)
result = result - bearing

rib1 = Pos(-plate_length/2 + rib_thickness/2, 0, 0) * Box(rib_thickness, rib_height, plate_thickness)
rib2 = Pos(plate_length/2 - rib_thickness/2, 0, 0) * Box(rib_thickness, rib_height, plate_thickness)
result = result + rib1 + rib2

part = result
part.name = "plate_with_notch_bearing_and_ribs"
export_step(part, "output.step")