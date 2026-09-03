from build123d import *

plate_length = 80.0
plate_width = 30.0
plate_thickness = 4.0
rib_width = 20.0
rib_height = 2.0
hole_diameter = 5.0
hole_spacing = 12.0
hole_offset_from_end = 10.0
chamfer_size = 1.0

solid_body = Box(plate_length, plate_width, plate_thickness)
solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_size)

rib = Pos(0, 0, plate_thickness) * Box(rib_width, rib_width, rib_height)
solid_body = solid_body + rib

for i in range(6):
    x = -plate_length/2 + hole_offset_from_end + i * hole_spacing
    hole = Pos(x, 0, plate_thickness + rib_height) * Cylinder(hole_diameter/2, plate_thickness + rib_height + 10)
    solid_body = solid_body - hole

part = solid_body
part.name = "plate_with_rib_and_holes"
export_step(part, "output.step")