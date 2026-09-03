from build123d import *

plate_length = 80.0
plate_width = 60.0
plate_thickness = 6.0
rib_length = 40.0
rib_width = 20.0
rib_height = 4.0
hole_diameter = 4.0
hole_spacing_x = 30.0
hole_spacing_y = 20.0
chamfer_size = 0.8
fillet_radius = 1.2

solid_body = Box(plate_length, plate_width, plate_thickness)
solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_size)

rib = Pos(0, 0, plate_thickness/2 + rib_height/2) * Box(rib_length, rib_width, rib_height)
solid_body = solid_body + rib

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = fillet(top_face.edges(), fillet_radius)

hole_r = hole_diameter / 2
hole_h = plate_thickness + rib_height + 2
for x, y in [(-hole_spacing_x, -hole_spacing_y/2), (0, -hole_spacing_y/2), (hole_spacing_x, -hole_spacing_y/2),
             (-hole_spacing_x, hole_spacing_y/2), (0, hole_spacing_y/2), (hole_spacing_x, hole_spacing_y/2)]:
    solid_body = solid_body - Pos(x, y, 0) * Cylinder(hole_r, hole_h)

part = solid_body
part.name = "plate_with_rib_and_holes"
export_step(part, "output.step")