from build123d import *

plate_length = 80.0
plate_width = 40.0
plate_thickness = 20.0
tab_length = 20.0
tab_width = 10.0
wall_thickness = 2.5
hole_diameter = 8.0
hole_spacing = 30.0
chamfer_size = 1.0
rib_thickness = 2.0
rib_height = 5.0

base_plate = Box(plate_length, plate_width, plate_thickness)
tab = Pos(plate_length/2 + tab_length/2, 0, 0) * Box(tab_length, tab_width, plate_thickness)
combined = base_plate + tab

vertical_edges = combined.edges().filter_by(Axis.Z)
chamfered = chamfer(vertical_edges, chamfer_size)

hollow = offset(chamfered, amount=-wall_thickness)

rib = Pos(0, 0, plate_thickness/2 - wall_thickness + rib_height/2) * Box(plate_length - 2*wall_thickness, rib_thickness, rib_height)
with_rib = hollow + rib

hole_positions = [
    (-hole_spacing/2, -hole_spacing/2),
    (hole_spacing/2, -hole_spacing/2),
    (-hole_spacing/2, hole_spacing/2),
    (hole_spacing/2, hole_spacing/2)
]

result = with_rib
for x, y in hole_positions:
    result = result - Pos(x, y, 0) * Cylinder(hole_diameter/2, plate_thickness + 10)

part = result
part.name = "plate_with_tab_rib_and_holes"
export_step(part, "output.step")