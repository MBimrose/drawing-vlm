from build123d import *

outer_diameter = 80.0
inner_diameter = 60.0
length = 80.0
wall_thickness = (outer_diameter - inner_diameter) / 2.0
slot_width = 10.0
slot_depth = wall_thickness * 0.8
slot_length = length * 0.6
chamfer_size = 1.0
hole_diameter = 5.0
hole_spacing = 30.0

outer_cyl = Cylinder(outer_diameter / 2.0, length)
inner_cyl = Cylinder(inner_diameter / 2.0, length)
result = outer_cyl - inner_cyl

slot_box = Box(slot_length, outer_diameter, slot_width)
result = result - slot_box

for x in [-hole_spacing / 2.0, hole_spacing / 2.0]:
    hole = Pos(x, 0, 0) * Rot(90, 0, 0) * Cylinder(hole_diameter / 2.0, outer_diameter)
    result = result - hole

result = chamfer(result.edges(), chamfer_size)

part = result
part.name = "hollow_cylinder_with_slot_and_holes"
export_step(part, "output.step")