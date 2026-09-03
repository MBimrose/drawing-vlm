from build123d import *

plate_length = 80.0
plate_width = 15.0
plate_thickness = 8.0
tab_length = 30.0
hole_diameter = 12.0
hole_center_offset = 5.0
rib_width = 10.0
rib_height = 4.0
chamfer_distance = 1.0

base_plate = Box(plate_length, plate_width, plate_thickness)
tab = Pos(plate_length/2 + tab_length/2, 0, 0) * Box(tab_length, plate_width, plate_thickness)
bracket_body = base_plate + tab

hole_center_x = plate_length/2 + tab_length - hole_center_offset
bracket_body = bracket_body - Pos(hole_center_x, plate_width/2, 0) * Cylinder(hole_diameter/2, plate_thickness * 2)

rib = Pos(0, 0, plate_thickness/2 - rib_height/2) * Box(rib_width, plate_width, rib_height)
bracket_body = bracket_body + rib

bracket_body = chamfer(bracket_body.edges(), chamfer_distance)

part = bracket_body
part.name = "bracket"
export_step(part, "output.step")