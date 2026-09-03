from build123d import *

plate_length = 80.0
plate_width = 60.0
plate_thickness = 5.0
rib_width = 5.0
rib_height = 3.0
rib_spacing = 10.0
pocket_length = 20.0
pocket_width = 10.0
pocket_depth = 2.5
hole_diameter = 5.0
chamfer_size = 1.0

rib_count = int((plate_length - rib_spacing) // (rib_width + rib_spacing))

solid_body = Box(plate_length, plate_width, plate_thickness)

for i in range(rib_count):
    x_offset = -plate_length/2 + rib_spacing + i*(rib_width + rib_spacing) + rib_width/2
    rib = Pos(x_offset, 0, -plate_thickness/2 + rib_height/2) * Box(rib_width, plate_width, rib_height)
    solid_body = solid_body + rib

pocket = Pos(0, plate_width/4, plate_thickness/2 - pocket_depth/2) * Box(pocket_length, pocket_width, pocket_depth)
solid_body = solid_body - pocket

hole = Pos(0, 0, 0) * Cylinder(hole_diameter/2, plate_thickness * 2)
solid_body = solid_body - hole

bottom_face = solid_body.faces().sort_by(Axis.Y)[0]
bottom_edges = bottom_face.edges()
solid_body = chamfer(bottom_edges, chamfer_size)

part = solid_body
part.name = "ribbed_plate_with_pocket"
export_step(part, "output.step")