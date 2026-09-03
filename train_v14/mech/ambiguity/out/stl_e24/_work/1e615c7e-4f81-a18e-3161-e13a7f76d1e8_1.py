from build123d import *

plate_width = 80.0
plate_depth = 50.0
plate_thickness = 6.0
tab_length = 30.0
tab_width = 20.0
hole_diameter = 12.0
fillet_radius = 2.0
rib_width = 30.0
rib_length = 50.0
rib_height = 4.0
rib_offset_x = 10.0

base = Pos(0, 0, plate_thickness / 2) * Box(plate_width, plate_depth, plate_thickness)
tab = Pos(plate_width / 2 + tab_length / 2, 0, plate_thickness / 2) * Box(tab_length, tab_width, plate_thickness)
solid_body = base + tab

hole = Pos(plate_width / 3, 0, plate_thickness / 2) * Cylinder(hole_diameter / 2, plate_thickness + 2)
solid_body = solid_body - hole

solid_body = fillet(solid_body.edges().filter_by(Axis.Z), fillet_radius)

rib = Pos(rib_offset_x, 0, plate_thickness + rib_height / 2) * Box(rib_width, rib_length, rib_height)
solid_body = solid_body + rib

part = solid_body
part.name = "plate_with_tab_rib"
export_step(part, "output.step")