from build123d import *

plate_width = 80.0
plate_length = 80.0
plate_thickness = 6.0
rib_width = 10.0
rib_height = 4.0
hole_diameter = 5.0
hole_spacing = 12.0
num_holes = 5
chamfer_size = 0.5

base = Box(plate_width, plate_length, plate_thickness)
rib = Pos(-plate_width/2 + rib_width/2, 0, 0) * Box(rib_width, rib_height, plate_thickness)
result = base + rib

for i in range(num_holes):
    x = -((num_holes-1)*hole_spacing)/2 + i * hole_spacing
    result = result - Pos(x, 0, 0) * Cylinder(hole_diameter/2, plate_thickness + 3)

top_face = result.faces().sort_by(Axis.Z)[-1]
top_edges = top_face.edges()
result = chamfer(top_edges, chamfer_size)

part = result
part.name = "plate_with_rib_and_holes"
export_step(part, "output.step")