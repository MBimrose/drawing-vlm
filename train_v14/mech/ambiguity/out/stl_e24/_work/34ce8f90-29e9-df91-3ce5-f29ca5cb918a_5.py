from build123d import *

plate_length = 80.0
plate_width = 60.0
plate_thickness = 6.0
rib_length = 40.0
rib_width = 20.0
rib_height = 4.0
rib_fillet_radius = 1.2
hole_diameter = 4.0
hole_spacing = 30.0
edge_chamfer = 0.8

base = Box(plate_length, plate_width, plate_thickness)
rib = Pos(0, 0, plate_thickness/2 + rib_height/2) * Box(rib_length, rib_width, rib_height)
result = base + rib

top_face = result.faces().sort_by(Axis.Z)[-1]
result = fillet(top_face.edges(), rib_fillet_radius)

hole_positions = [
    (-hole_spacing, 0),
    (0, 0),
    (hole_spacing, 0),
    (-plate_length/2 + 10, -plate_width/2 + 20),
    (-plate_length/2 + 10, plate_width/2 - 20),
]
for x, y in hole_positions:
    result = result - Pos(x, y, 0) * Cylinder(hole_diameter/2, plate_thickness + rib_height + 10)

vertical_edges = result.edges().filter_by(Axis.Z)
result = chamfer(vertical_edges, edge_chamfer)

part = result
part.name = "plate_with_rib_and_holes"
export_step(part, "output.step")