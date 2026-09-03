from build123d import *

plate_length = 80.0
plate_width = 60.0
plate_thickness = 5.0
pocket_length = 50.0
pocket_width = 30.0
pocket_depth = 2.5
hole_diameter = 7.0
hole_spacing = 30.0
hole_offset_from_edge = 10.0
rib_thickness = 3.0
rib_height = 2.0
chamfer_size = 0.4
fillet_radius = 0.5

solid_body = Box(plate_length, plate_width, plate_thickness)

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = chamfer(top_face.edges(), chamfer_size)

pocket = Pos(0, 0, plate_thickness/2 - pocket_depth/2) * Box(pocket_length, pocket_width, pocket_depth)
solid_body = solid_body - pocket

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = fillet(top_face.edges(), fillet_radius)

hole_y = plate_width/2 - hole_offset_from_edge
for x in [-hole_spacing, 0, hole_spacing]:
    solid_body = solid_body - Pos(x, hole_y, 0) * Cylinder(hole_diameter/2, plate_thickness)

rib = Pos(0, 0, rib_height/2) * Box(rib_thickness, plate_width, rib_height)
solid_body = solid_body + rib

part = solid_body
part.name = "plate_with_pocket_rib_holes"
export_step(part, "output.step")