from build123d import *

plate_width = 80.0
plate_length = 80.0
plate_thickness = 6.0
rib_width = 6.0
rib_length = 60.0
rib_height = 2.0
hole_diameter = 5.0
hole_depth = 4.5
hole_spacing = 12.0
num_holes = 5
chamfer_size = 0.5

base = Box(plate_width, plate_length, plate_thickness)
rib = Pos(0, 0, -plate_thickness/2 + rib_height/2) * Box(rib_width, rib_length, rib_height)
solid_body = base + rib

for i in range(num_holes):
    x = (i - (num_holes - 1) / 2) * hole_spacing
    solid_body = solid_body - Pos(x, 0, plate_thickness/2 - hole_depth/2) * Cylinder(hole_diameter/2, hole_depth)

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = chamfer(top_face.edges(), chamfer_size)

part = solid_body
part.name = "plate_with_rib_and_holes"
export_step(part, "output.step")