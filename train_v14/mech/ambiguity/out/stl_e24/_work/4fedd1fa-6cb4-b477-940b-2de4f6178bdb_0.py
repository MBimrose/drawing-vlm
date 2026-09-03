from build123d import *

plate_width = 60.0
plate_length = 60.0
plate_thickness = 8.0
slot_length = 30.0
slot_width = 10.0
hole_diameter = 10.0
chamfer_distance = 2.0
tab_width = 12.0
tab_height = 6.0
tab_thickness = 4.0

solid_body = Box(plate_width, plate_length, plate_thickness)
solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_distance)
solid_body = solid_body - Box(slot_length, slot_width, plate_thickness)
solid_body = solid_body - Cylinder(hole_diameter / 2, plate_thickness)
solid_body = solid_body + Pos(plate_width / 2 + tab_width / 2, 0, 0) * Box(tab_width, tab_height, tab_thickness)
solid_body = solid_body + Pos(-plate_width / 2 - tab_width / 2, 0, 0) * Box(tab_width, tab_height, tab_thickness)

part = solid_body
part.name = "plate_with_tabs"
export_step(part, "output.step")