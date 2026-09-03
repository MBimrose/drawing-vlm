from build123d import *

outer_diameter = 80.0
inner_diameter = 30.0
height = 20.0
wall_thickness = (outer_diameter - inner_diameter) / 2.0
rib_width = 6.0
rib_height = 20.0
rib_thickness = 4.0
rib_chamfer = 0.5
hole_diameter = 2.0
hole_offset_radius = (inner_diameter / 2.0 + outer_diameter / 2.0) / 2.0
slot_width = 6.0
slot_height = 12.0
slot_offset_radius = (inner_diameter / 2.0 + outer_diameter / 2.0) / 2.0

outer_radius = outer_diameter / 2.0
inner_radius = inner_diameter / 2.0

solid_body = Cylinder(outer_radius, height) - Cylinder(inner_radius, height)

rib = Pos(outer_radius + rib_thickness / 2.0, 0, height / 2.0) * Box(rib_thickness, rib_width, rib_height)
rib = chamfer(rib.edges(), rib_chamfer)
solid_body = solid_body + rib

solid_body = solid_body - Pos(hole_offset_radius, 0, 0) * Cylinder(hole_diameter / 2.0, height)

slot = Pos(slot_offset_radius, 0, 0) * Box(slot_width, slot_height, height)
solid_body = solid_body - slot

part = solid_body
part.name = "hollow_cylinder_with_rib"
export_step(part, "output.step")