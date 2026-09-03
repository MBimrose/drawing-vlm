from build123d import *

plate_length = 80.0
plate_width = 60.0
plate_thickness = 8.0
pocket_length = 40.0
pocket_width = 30.0
hole_diameter = 4.0
hole_depth = 6.0
hole_spacing_x = 20.0
hole_spacing_y = 15.0
fillet_radius = 2.0
chamfer_distance = 1.0
rib_height = 4.0
rib_thickness = 2.0

base = Box(plate_length, plate_width, plate_thickness)
base = fillet(base.edges().filter_by(Axis.Z), fillet_radius)
base = chamfer(base.edges(), chamfer_distance)

pocket = Box(pocket_length, pocket_width, plate_thickness)
base = base - pocket

rib = Pos(0, plate_width/2 - rib_thickness/2, 0) * Box(rib_height, rib_thickness, plate_thickness)
base = base + rib

hole_positions = [
    (-hole_spacing_x, -hole_spacing_y),
    (0, -hole_spacing_y),
    (hole_spacing_x, -hole_spacing_y),
    (-hole_spacing_x, hole_spacing_y),
    (0, hole_spacing_y),
    (hole_spacing_x, hole_spacing_y),
]
for x, y in hole_positions:
    base = base - Pos(x, y, plate_thickness/2 - hole_depth/2) * Cylinder(hole_diameter/2, hole_depth)

part = base
part.name = "plate_with_pocket_rib_holes"
export_step(part, "output.step")