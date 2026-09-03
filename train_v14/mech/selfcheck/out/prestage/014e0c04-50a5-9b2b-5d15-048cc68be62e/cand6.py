from build123d import *

plate_length = 80.0
plate_width = 40.0
plate_thickness = 6.0
notch_radius = 10.0
notch_depth = 6.0
rib_width = 6.0
rib_height = 3.0
rib_length = plate_length - 10.0
hole_diameter = 5.0
hole_spacing = 50.0
chamfer_size = 0.5

solid_body = Box(plate_length, plate_width, plate_thickness)

notch = Pos(0, plate_width/2 - notch_depth/2, 0) * Rot(90, 0, 0) * Cylinder(notch_radius, notch_depth)
solid_body = solid_body - notch

vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = chamfer(vertical_edges, chamfer_size)

rib = Pos(0, 0, plate_thickness/2 + rib_height/2) * Box(rib_width, rib_length, rib_height)
solid_body = solid_body + rib

for x in [-hole_spacing/2, hole_spacing/2]:
    hole = Pos(x, 0, 0) * Cylinder(hole_diameter/2, plate_thickness + rib_height + 10)
    solid_body = solid_body - hole

part = solid_body
part.name = "plate_with_notch_rib_and_holes"
export_step(part, "output.step")