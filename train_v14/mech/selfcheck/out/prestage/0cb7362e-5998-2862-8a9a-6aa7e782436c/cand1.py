from build123d import *

length = 80.0
width = 30.0
thickness = 10.0
rib_width = 20.0
rib_height = 6.0
hole_diameter = 4.0
cbore_diameter = 7.0
cbore_depth = 2.0
hole_spacing = 12.0
hole_count = 5
chamfer_size = 1.0

base = Pos(0, 0, thickness/2) * Box(length, width, thickness)
rib = Pos(0, 0, thickness/2) * Box(rib_width, rib_height, thickness)
solid_body = base + rib

start_x = -length/2 + hole_spacing
for i in range(hole_count):
    x = start_x + i * hole_spacing
    solid_body = solid_body - Pos(x, 0, thickness/2) * Cylinder(hole_diameter/2, thickness + 1)
    solid_body = solid_body - Pos(x, 0, cbore_depth/2) * Cylinder(cbore_diameter/2, cbore_depth)

solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_size)

part = solid_body
part.name = "ribbed_plate_with_cbore_holes"
export_step(part, "output.step")