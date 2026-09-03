from build123d import *

plate_width = 50.0
plate_length = 50.0
plate_thickness = 8.0
rib_width = 10.0
rib_length = 30.0
rib_height = 4.0
hole_diameter = 12.0
chamfer_distance = 2.0

base = Box(plate_width, plate_length, plate_thickness)
rib = Box(rib_width, rib_length, rib_height)
combined = base + rib

hole = Cylinder(hole_diameter / 2, plate_thickness + rib_height + 10)
combined = combined - hole

top_face = combined.faces().sort_by(Axis.Z)[-1]
top_edges = top_face.edges()
combined = chamfer(top_edges, chamfer_distance)

part = combined
part.name = "plate_with_rib_and_hole"
export_step(part, "output.step")