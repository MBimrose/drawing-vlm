from build123d import *

rail_length = 100.0
rail_width = 30.0
rail_height = 20.0
wall_thickness = 3.0
slot_width = 6.0
slot_depth = 10.0
slot_length = 80.0
fillet_radius = 2.0
hole_diameter = 5.0
hole_offset_from_end = 12.0
hole_offset_from_bottom = 8.0

base = Box(rail_length, rail_width, rail_height)
base = fillet(base.edges(), fillet_radius)

inner = Box(rail_length - 2*wall_thickness, rail_width - 2*wall_thickness, rail_height - 2*wall_thickness)
result = base - inner

slot = Box(slot_length, slot_depth, slot_width)
result = result - slot

hole_x = rail_length/2 - hole_offset_from_end
hole_y = -rail_width/2 + hole_offset_from_bottom
hole = Pos(hole_x, hole_y, 0) * Cylinder(hole_diameter/2, rail_height)
result = result - hole

part = result
part.name = "rail_with_slot_and_hole"
export_step(part, "output.step")