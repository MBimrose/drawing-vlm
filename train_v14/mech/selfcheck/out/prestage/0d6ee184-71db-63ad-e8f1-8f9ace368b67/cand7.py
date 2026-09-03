from build123d import *

plate_width = 70.0
plate_depth = 30.0
plate_thickness = 10.0
tab_width = 40.0
tab_height = 12.0
hole_diameter = 5.0
hole_spacing_x = 30.0
hole_spacing_y = 20.0
fillet_radius = 2.0

base = Box(plate_width, plate_depth, plate_thickness)
tab = Pos(0, plate_depth/2 + tab_height/2, 0) * Box(tab_width, tab_height, plate_thickness)
solid_body = base + tab

hole_positions = [
    (-hole_spacing_x/2, -hole_spacing_y/2),
    (hole_spacing_x/2, -hole_spacing_y/2),
    (0, hole_spacing_y/2)
]
for x, y in hole_positions:
    solid_body = solid_body - Pos(x, y, 0) * Cylinder(hole_diameter/2, plate_thickness + 1)

vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = fillet(vertical_edges, fillet_radius)

part = solid_body
part.name = "plate_with_tab_and_holes"
export_step(part, "output.step")