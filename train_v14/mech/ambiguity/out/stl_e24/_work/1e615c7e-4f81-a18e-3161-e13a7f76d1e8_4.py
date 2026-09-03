from build123d import *

plate_length = 80.0
plate_width = 50.0
plate_thickness = 6.0
tab_length = 30.0
tab_width = 20.0
rib_width = 30.0
rib_height = 4.0
rib_offset = plate_length / 3.0
hole_diameter = 12.0
countersink_diameter = 16.0
countersink_depth = 2.0
fillet_radius = 2.0

base_plate = Pos(0, 0, plate_thickness / 2) * Box(plate_length, plate_width, plate_thickness)
tab = Pos(plate_length / 2 + tab_length / 2, 0, plate_thickness / 2) * Box(tab_length, tab_width, plate_thickness)
rib = Pos(rib_offset - plate_length / 2, 0, plate_thickness + rib_height / 2) * Box(rib_width, plate_width, rib_height)

solid_body = base_plate + tab + rib
solid_body = fillet(solid_body.edges().filter_by(Axis.Z), fillet_radius)

hole_center_x = plate_length / 2 + tab_length / 2
hole_center_y = 0.0
hole_z = plate_thickness + rib_height

hole = Pos(hole_center_x, hole_center_y, hole_z) * CounterSinkHole(hole_diameter / 2, countersink_diameter / 2, plate_thickness + rib_height + 10, 90)
solid_body = solid_body - hole

part = solid_body
part.name = "plate_with_tab_rib_and_hole"
export_step(part, "output.step")