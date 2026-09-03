from build123d import *

outer_diameter = 80.0
inner_diameter = 60.0
length = 80.0
wall_thickness = (outer_diameter - inner_diameter) / 2.0
slot_width = 20.0
slot_height = 10.0
slot_depth = wall_thickness + 2.0
hole_diameter = 5.0
hole_spacing = 30.0
hole_offset = 15.0
chamfer_size = 1.0

outer_cyl = Cylinder(outer_diameter / 2.0, length)
inner_cyl = Cylinder(inner_diameter / 2.0, length)
base = outer_cyl - inner_cyl

slot = Pos(0, 0, slot_depth / 2.0) * Box(slot_width, length, slot_depth)
base = base - slot

hole_r = hole_diameter / 2.0
hole_h = length + 2.0
for x in [-hole_spacing / 2.0, hole_spacing / 2.0]:
    base = base - Pos(x, outer_diameter / 2.0, 0) * Cylinder(hole_r, hole_h)
    base = base - Pos(x, -outer_diameter / 2.0, 0) * Cylinder(hole_r, hole_h)

base = chamfer(base.edges(), chamfer_size)

part = base
part.name = "hollow_cylinder_with_slot_and_holes"
export_step(part, "output.step")