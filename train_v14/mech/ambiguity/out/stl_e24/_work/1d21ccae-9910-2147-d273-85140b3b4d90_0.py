from build123d import *

plate_length = 100.0
plate_width = 70.0
plate_thickness = 5.0
opening_length = 60.0
opening_width = 40.0
corner_fillet_radius = 2.0
hole_diameter = 4.0
hole_offset = 10.0
rib_thickness = 2.0
rib_height = 3.0

base = Box(plate_length, plate_width, plate_thickness)
opening = Box(opening_length, opening_width, plate_thickness)
result = base - opening

result = fillet(result.edges().filter_by(Axis.Z), corner_fillet_radius)

hole_positions = [
    (-plate_length/2 + hole_offset, -plate_width/2 + hole_offset),
    ( plate_length/2 - hole_offset, -plate_width/2 + hole_offset),
    (-plate_length/2 + hole_offset,  plate_width/2 - hole_offset),
    ( plate_length/2 - hole_offset,  plate_width/2 - hole_offset)
]
for x, y in hole_positions:
    result = result - Pos(x, y, 0) * Cylinder(hole_diameter/2, plate_thickness)

rib = Box(rib_thickness, plate_width, rib_height)
rib_left = Pos(-plate_length/2 + rib_thickness/2, 0, plate_thickness + rib_height/2) * rib
rib_right = Pos(plate_length/2 - rib_thickness/2, 0, plate_thickness + rib_height/2) * rib
result = result + rib_left + rib_right

part = result
part.name = "plate_with_opening_ribs"
export_step(part, "output.step")