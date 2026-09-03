from build123d import *

plate_length = 80.0
plate_width = 30.0
plate_thickness = 3.0
rib_height = 2.0
rib_width = 5.0
rib_offset = 5.0
hole_diameter = 2.0
cbore_diameter = 4.0
cbore_depth = 2.0
chamfer_size = 0.2

base = Box(plate_length, plate_width, plate_thickness)
rib = Pos(-plate_length/2 + rib_offset + rib_width/2, 0, 0) * Box(rib_width, rib_height, plate_thickness)
solid_body = base + rib

shaft = Cylinder(hole_diameter/2, plate_thickness + 1)
cbore = Pos(0, 0, plate_thickness/2 - cbore_depth/2) * Cylinder(cbore_diameter/2, cbore_depth)
solid_body = solid_body - shaft - cbore

solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_size)

part = solid_body
part.name = "plate_with_rib_and_cbore"
export_step(part, "output.step")