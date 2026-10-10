from build123d import *

base_width = 60.0
base_depth = 40.0
base_thickness = 8.0
shaft_diameter = 12.0
shaft_length = 70.0
tip_length = 10.0
chamfer_size = 1.5
hole_diameter = 6.0
hole_offset_x = 18.0
hole_offset_y = 8.0

base = Pos(0, 0, base_thickness/2) * Box(base_width, base_depth, base_thickness)
base = chamfer(base.edges(), chamfer_size)

shaft = Pos(0, 0, base_thickness + shaft_length/2) * Cylinder(shaft_diameter/2, shaft_length)
tip = Pos(0, 0, base_thickness + shaft_length + tip_length/2) * Cone(shaft_diameter/2, 0, tip_length)

solid_body = base + shaft + tip

hole_r = hole_diameter / 2
hole_h = base_thickness + 2
for x, y in [(hole_offset_x, hole_offset_y), (-hole_offset_x, hole_offset_y),
             (hole_offset_x, -hole_offset_y), (-hole_offset_x, -hole_offset_y)]:
    solid_body = solid_body - Pos(x, y, base_thickness/2) * Cylinder(hole_r, hole_h)

part = solid_body
part.name = "base_with_shaft_tip_and_holes"
export_step(part, "output.step")