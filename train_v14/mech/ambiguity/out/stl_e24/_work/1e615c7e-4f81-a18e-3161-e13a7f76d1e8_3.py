from build123d import *

plate_length = 80.0
plate_width = 50.0
plate_thickness = 6.0
tab_length = 30.0
tab_width = 20.0
rib_height = 4.0
rib_length = plate_length / 3.0
hole_diameter = 12.0
hole_depth = plate_thickness + rib_height + 1.0
fillet_radius = 2.0

base_plate = Pos(0, 0, plate_thickness/2) * Box(plate_length, plate_width, plate_thickness)
tab = Pos(plate_length/2 + tab_length/2, 0, plate_thickness/2) * Box(tab_length, tab_width, plate_thickness)
rib = Pos(0, 0, plate_thickness + rib_height/2) * Box(rib_length, plate_width, rib_height)

solid_body = base_plate + tab + rib

hole_center_x = plate_length / 3.0
hole_center_y = 0.0
hole = Pos(hole_center_x, hole_center_y, plate_thickness + rib_height - hole_depth/2) * Cylinder(hole_diameter/2, hole_depth)
solid_body = solid_body - hole

solid_body = fillet(solid_body.edges().filter_by(Axis.Z), fillet_radius)

part = solid_body
part.name = "plate_with_tab_rib_and_hole"
export_step(part, "output.step")