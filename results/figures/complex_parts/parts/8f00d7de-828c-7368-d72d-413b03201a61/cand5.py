from build123d import *

plate_length = 60.0
plate_width = 40.0
plate_thickness = 8.0
shaft_diameter = 12.0
shaft_length = 52.0
tip_length = 20.0
hole_diameter = 6.0
hole_offset = 12.0
chamfer_distance = 1.5

base = Box(plate_length, plate_width, plate_thickness)
base = chamfer(base.edges(), chamfer_distance)

shaft = Pos(0, 0, plate_thickness/2 + shaft_length/2) * Cylinder(shaft_diameter/2, shaft_length)
tip = Pos(0, 0, plate_thickness/2 + shaft_length + tip_length/2) * Cone(shaft_diameter/2, 0, tip_length)

result = base + shaft + tip

hole_positions = [
    (-plate_length/2 + hole_offset, -plate_width/2 + hole_offset),
    ( plate_length/2 - hole_offset, -plate_width/2 + hole_offset),
    (-plate_length/2 + hole_offset,  plate_width/2 - hole_offset),
    ( plate_length/2 - hole_offset,  plate_width/2 - hole_offset),
]

for x, y in hole_positions:
    result = result - Pos(x, y, 0) * Cylinder(hole_diameter/2, plate_thickness + 2)

part = result
part.name = "plate_with_shaft_and_holes"
export_step(part, "output.step")