from build123d import *

plate_width = 60.0
plate_depth = 40.0
plate_thickness = 8.0
shaft_diameter = 12.0
shaft_height = 52.0
tip_height = 20.0
chamfer_size = 1.5
hole_diameter = 6.0
hole_offset = 12.0

base = Pos(0, 0, plate_thickness/2) * Box(plate_width, plate_depth, plate_thickness)
base = chamfer(base.edges(), chamfer_size)

shaft = Pos(0, 0, plate_thickness + shaft_height/2) * Cylinder(shaft_diameter/2, shaft_height)
tip = Pos(0, 0, plate_thickness + shaft_height + tip_height/2) * Cone(shaft_diameter/2, 0, tip_height)

result = base + shaft + tip

hole_positions = [
    (-plate_width/2 + hole_offset, -plate_depth/2 + hole_offset),
    (plate_width/2 - hole_offset, -plate_depth/2 + hole_offset),
    (-plate_width/2 + hole_offset, plate_depth/2 - hole_offset),
    (plate_width/2 - hole_offset, plate_depth/2 - hole_offset),
]

for x, y in hole_positions:
    result = result - Pos(x, y, plate_thickness/2) * Cylinder(hole_diameter/2, plate_thickness + 1)

part = result
part.name = "plate_with_shaft_and_holes"
export_step(part, "output.step")