from build123d import *

lever_length = 100.0
lever_width = 15.0
lever_thickness = 8.0
pivot_radius = 6.0
chamfer_dist = 1.0

base = Box(lever_length, lever_width, lever_thickness)
pivot = Pos(lever_length/2, 0, 0) * Cylinder(pivot_radius, lever_thickness)
solid_body = base + pivot
solid_body = chamfer(solid_body.edges(), chamfer_dist)

part = solid_body
part.name = "lever"
export_step(part, "output.step")