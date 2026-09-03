from build123d import *

plate_length = 80.0
plate_width = 50.0
plate_thickness = 8.0
edge_fillet_radius = 3.0
pad_diameter = 30.0
pad_depth = 2.0
hole_diameter = 8.0
hole_spacing_x = 30.0
hole_spacing_y = 24.0
rib_width = 6.0
rib_height = 4.0

base = Box(plate_length, plate_width, plate_thickness)
rib = Box(plate_length, rib_width, rib_height)
solid_body = base + rib

vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = fillet(vertical_edges, edge_fillet_radius)

pad = Pos(0, 0, plate_thickness/2 - pad_depth/2) * Cylinder(pad_diameter/2, pad_depth)
solid_body = solid_body - pad

hole_positions = [
    (-hole_spacing_x/2, -hole_spacing_y/2),
    ( hole_spacing_x/2, -hole_spacing_y/2),
    (-hole_spacing_x/2,  hole_spacing_y/2),
    ( hole_spacing_x/2,  hole_spacing_y/2),
]
for x, y in hole_positions:
    hole = Pos(x, y, 0) * Cylinder(hole_diameter/2, plate_thickness * 2)
    solid_body = solid_body - hole

part = solid_body
part.name = "plate_with_rib_and_holes"
export_step(part, "output.step")