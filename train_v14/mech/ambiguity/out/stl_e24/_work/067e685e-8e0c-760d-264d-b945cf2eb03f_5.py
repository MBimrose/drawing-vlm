from build123d import *

plate_length = 80.0
plate_width = 30.0
plate_thickness = 5.0
fillet_radius = 2.5
chamfer_distance = 0.5
hole_diameter = 4.0
hole_spacing_x = 30.0
hole_spacing_y = 20.0
rib_width = 4.0
rib_height = 3.0
rib_spacing = 10.0

solid_body = Box(plate_length, plate_width, plate_thickness)

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = fillet(top_face.edges(), fillet_radius)

bottom_face = solid_body.faces().sort_by(Axis.Z)[0]
solid_body = chamfer(bottom_face.edges(), chamfer_distance)

for x, y in [(-hole_spacing_x/2, -hole_spacing_y/2), (hole_spacing_x/2, -hole_spacing_y/2),
             (-hole_spacing_x/2, hole_spacing_y/2), (hole_spacing_x/2, hole_spacing_y/2)]:
    solid_body = solid_body - Pos(x, y, 0) * Cylinder(hole_diameter/2, plate_thickness * 2)

for x, y in [(-rib_spacing/2, 0), (rib_spacing/2, 0)]:
    solid_body = solid_body + Pos(x, y, plate_thickness/2 + rib_height/2) * Box(rib_width, rib_height, rib_height)

part = solid_body
part.name = "plate_with_ribs_and_holes"
export_step(part, "output.step")