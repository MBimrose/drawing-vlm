from build123d import *

width = 60.0
depth = 40.0
thickness = 5.0
rib_width = 48.0
rib_height = 8.0
rib_thickness = 3.0
slot_width = 20.0
slot_height = 4.0
slot_offset_x = 5.0
slot_offset_y = 10.0
hole_diameter = 5.0

base = Pos(0, 0, thickness/2) * Box(width, depth, thickness)
rib = Pos(0, depth/2 + rib_thickness/2, thickness/2) * Box(rib_width, rib_thickness, rib_height)
solid = base + rib

slot = Pos(-width/2 + slot_offset_x + slot_width/2, depth/2 - slot_offset_y - slot_height/2, thickness/2) * Box(slot_width, slot_height, thickness)
solid = solid - slot

hole = Pos(0, depth/2 + rib_thickness/2, thickness/2) * Cylinder(hole_diameter/2, rib_height)
solid = solid - hole

part = solid
part.name = "ZSpacer"
export_step(part, "output.step")