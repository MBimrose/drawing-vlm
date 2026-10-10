from build123d import *

base_width = 60.0
base_depth = 40.0
base_thickness = 8.0
shaft_diameter = 12.0
shaft_height = 52.0
tip_height = 20.0
chamfer_distance = 1.5
hole_diameter = 6.0
hole_offset = 12.0

base = Pos(0, 0, base_thickness/2) * Box(base_width, base_depth, base_thickness)
base = chamfer(base.edges(), chamfer_distance)

shaft = Pos(0, 0, base_thickness + shaft_height/2) * Cylinder(shaft_diameter/2, shaft_height)
tip = Pos(0, 0, base_thickness + shaft_height + tip_height/2) * Cone(shaft_diameter/2, 0, tip_height)

solid_body = base + shaft + tip

hole_positions = [
    (-base_width/2 + hole_offset, -base_depth/2 + hole_offset),
    ( base_width/2 - hole_offset, -base_depth/2 + hole_offset),
    (-base_width/2 + hole_offset,  base_depth/2 - hole_offset),
    ( base_width/2 - hole_offset,  base_depth/2 - hole_offset)
]

for x, y in hole_positions:
    solid_body = solid_body - Pos(x, y, base_thickness/2) * Cylinder(hole_diameter/2, base_thickness + 1)

part = solid_body
part.name = "base_with_shaft_tip_and_holes"
export_step(part, "output.step")