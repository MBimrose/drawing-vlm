from build123d import *

plate_length = 100.0
plate_width = 70.0
plate_thickness = 5.0
pocket_length = 60.0
pocket_width = 40.0
fillet_radius = 2.0
hole_diameter = 5.0
hole_offset = 10.0
rib_thickness = 2.0
rib_height = 3.0

base = Box(plate_length, plate_width, plate_thickness)
pocket = Box(pocket_length, pocket_width, plate_thickness)
base = base - pocket

base = fillet(base.edges().filter_by(Axis.Z), fillet_radius)

hole_positions = [
    (hole_offset, hole_offset),
    (plate_length - hole_offset, hole_offset),
    (hole_offset, plate_width - hole_offset),
    (plate_length - hole_offset, plate_width - hole_offset),
]
for x, y in hole_positions:
    base = base - Pos(x, y, 0) * Cylinder(hole_diameter/2, plate_thickness)

rib = Box(rib_thickness, plate_width, rib_height)
rib_left = Pos(-plate_length/2 + rib_thickness/2, 0, plate_thickness + rib_height/2) * rib
rib_right = Pos(plate_length/2 - rib_thickness/2, 0, plate_thickness + rib_height/2) * rib
base = base + rib_left + rib_right

part = base
part.name = "plate_with_pocket_ribs"
export_step(part, "output.step")