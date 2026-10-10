from build123d import *

base_width = 60.0
base_depth = 40.0
base_thickness = 8.0
base_chamfer = 1.5
slot_width = 20.0
slot_depth = 10.0
slot_offset = 5.0
hole_diameter = 6.0
hole_spacing_x = 12.0
hole_spacing_y = 12.0
hole_rows = 2
hole_cols = 3
shaft_radius = 6.0
shaft_length = 60.0
tip_length = 12.0

with BuildPart() as p:
    with BuildSketch() as s:
        Rectangle(base_width, base_depth)
    extrude(amount=base_thickness)

solid_body = p.part
solid_body = chamfer(solid_body.edges(), base_chamfer)

slot_center_y = -base_depth/2 + slot_offset + slot_depth/2
slot = Pos(0, slot_center_y, base_thickness/2) * Box(slot_width, slot_depth, base_thickness)
solid_body = solid_body - slot

for i in range(hole_cols):
    for j in range(hole_rows):
        x = (i - (hole_cols-1)/2) * hole_spacing_x
        y = (j - (hole_rows-1)/2) * hole_spacing_y
        solid_body = solid_body - Pos(x, y, base_thickness/2) * Cylinder(hole_diameter/2, base_thickness)

shaft = Pos(0, 0, base_thickness + shaft_length/2) * Cylinder(shaft_radius, shaft_length)
solid_body = solid_body + shaft

tip = Pos(0, 0, base_thickness + shaft_length + tip_length/2) * Cone(shaft_radius, 0, tip_length)
solid_body = solid_body + tip

part = solid_body
part.name = "base_with_shaft_and_tip"
export_step(part, "output.step")