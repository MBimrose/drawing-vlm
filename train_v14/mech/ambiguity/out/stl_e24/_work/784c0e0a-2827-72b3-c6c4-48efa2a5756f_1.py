from build123d import *

jaw_length = 80.0
jaw_width = 30.0
jaw_thickness = 10.0
rib_height = 4.0
rib_width = 5.0
rib_margin = 5.0
hole_diameter = 5.0
hole_offset = 10.0
fillet_radius = 1.0
chamfer_distance = 0.5
pocket_depth = 6.0
pocket_width = 12.0
pocket_height = 8.0

base = Box(jaw_length, jaw_width, jaw_thickness)
rib = Pos(0, 0, jaw_thickness/2 - rib_height/2) * Box(jaw_length - 2*rib_margin, rib_width, rib_height)
result = base + rib

for x, y in [(-jaw_length/2 + hole_offset, 0), (jaw_length/2 - hole_offset, 0)]:
    result = result - Pos(x, y, 0) * Cylinder(hole_diameter/2, jaw_thickness + 1)

result = result - Pos(0, 0, jaw_thickness/2 - pocket_depth/2) * Box(pocket_width, pocket_height, pocket_depth)

result = fillet(result.edges().filter_by(Axis.X), fillet_radius)
result = chamfer(result.faces().sort_by(Axis.Z)[-1].edges(), chamfer_distance)

part = result
part.name = "jaw_with_rib"
export_step(part, "output.step")