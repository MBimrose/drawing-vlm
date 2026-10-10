from build123d import *

base_width = 60.0
base_depth = 40.0
base_thickness = 8.0
pin_diameter = 12.0
pin_length = 52.0
tip_length = 20.0
chamfer_size = 1.5
hole_diameter = 6.0
hole_offset = 12.0

base = Pos(0, 0, base_thickness/2) * Box(base_width, base_depth, base_thickness)
base = chamfer(base.edges(), chamfer_size)

pin = Pos(0, 0, base_thickness + pin_length/2) * Cylinder(pin_diameter/2, pin_length)
tip = Pos(0, 0, base_thickness + pin_length + tip_length/2) * Cone(pin_diameter/2, 0, tip_length)

result = base + pin + tip

hole_positions = [
    (-base_width/2 + hole_offset, -base_depth/2 + hole_offset),
    ( base_width/2 - hole_offset, -base_depth/2 + hole_offset),
    (-base_width/2 + hole_offset,  base_depth/2 - hole_offset),
    ( base_width/2 - hole_offset,  base_depth/2 - hole_offset),
]

for x, y in hole_positions:
    result = result - Pos(x, y, 0) * Cylinder(hole_diameter/2, 200)

part = result
part.name = "pin_with_base_and_holes"
export_step(part, "output.step")