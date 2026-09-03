from build123d import *

outer_diameter = 80.0
height = 20.0
wall_thickness = 5.0
slot_width = 6.0
slot_depth = wall_thickness - 0.5
set_screw_diameter = 3.0
set_screw_head_diameter = 5.5
set_screw_head_depth = 2.0

outer_radius = outer_diameter / 2.0
inner_radius = outer_radius - wall_thickness

solid_body = Cylinder(outer_radius, height) - Cylinder(inner_radius, height)

slot_box = Pos(outer_radius - slot_depth / 2.0, 0, 0) * Box(slot_depth, slot_width, height)
solid_body = solid_body - slot_box

hole_cyl = Pos(outer_radius - slot_depth / 2.0, 0, 0) * Rot(0, 90, 0) * Cylinder(set_screw_diameter / 2.0, slot_depth)
solid_body = solid_body - hole_cyl

part = solid_body
part.name = "hollow_cylinder_with_slot_and_hole"
export_step(part, "output.step")