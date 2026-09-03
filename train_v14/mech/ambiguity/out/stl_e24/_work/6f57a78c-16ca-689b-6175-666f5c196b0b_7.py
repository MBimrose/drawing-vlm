from build123d import *

outer_diameter = 80.0
inner_diameter = 60.0
length = 80.0
wall_thickness = (outer_diameter - inner_diameter) / 2.0
slot_width = 20.0
slot_height = 10.0
chamfer_size = 1.0

outer_radius = outer_diameter / 2.0
inner_radius = inner_diameter / 2.0

shell = Cylinder(outer_radius, length) - Cylinder(inner_radius, length)

slot_box = Box(slot_width, outer_diameter * 2, slot_height)
shell = shell - slot_box

shell = chamfer(shell.edges(), chamfer_size)

part = shell
part.name = "hollow_cylinder_with_slot"
export_step(part, "output.step")