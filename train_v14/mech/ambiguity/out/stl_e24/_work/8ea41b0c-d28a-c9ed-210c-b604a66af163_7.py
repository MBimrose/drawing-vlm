from build123d import *

plate_width = 80.0
plate_height = 60.0
plate_thickness = 5.0
slot_width = 12.0
slot_height = 30.0
slot_offset_x = 20.0
slot_offset_y = 0.0
hole_diameter = 6.0
hole_spacing = 20.0
tab_width = 10.0
tab_height = 8.0

solid_body = Box(plate_width, plate_height, plate_thickness)

slot_center_x = -plate_width/2 + slot_offset_x + slot_width/2
slot_center_y = slot_offset_y
solid_body = solid_body - Pos(slot_center_x, slot_center_y, 0) * Box(slot_width, slot_height, plate_thickness)

hole_positions = [
    (-plate_width/2 + hole_spacing, -plate_height/2 + hole_spacing),
    (-plate_width/2 + 2*hole_spacing, -plate_height/2 + hole_spacing),
    (-plate_width/2 + 1.5*hole_spacing, -plate_height/2 + 2*hole_spacing),
]
for x, y in hole_positions:
    solid_body = solid_body - Pos(x, y, 0) * Cylinder(hole_diameter/2, plate_thickness)

right_tab = Pos(plate_width/2 - plate_thickness/2, 0, 0) * Box(plate_thickness, tab_width, tab_height)
solid_body = solid_body + right_tab

left_tab = Pos(-plate_width/2 + plate_thickness/2, 0, 0) * Box(plate_thickness, tab_width, tab_height)
solid_body = solid_body + left_tab

part = solid_body
part.name = "plate_with_slot_holes_and_tabs"
export_step(part, "output.step")