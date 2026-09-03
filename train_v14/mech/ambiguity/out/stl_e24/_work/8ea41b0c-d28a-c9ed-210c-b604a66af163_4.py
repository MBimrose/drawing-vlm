from build123d import *

bracket_width = 80.0
bracket_height = 60.0
bracket_thickness = 5.0
slot_width = 12.0
slot_height = 30.0
notch_width = 10.0
notch_height = 15.0
notch_offset_from_top = 5.0
hole_diameter = 6.0
hole_spacing = 20.0
hole_offset_x = 15.0
hole_offset_y = 15.0
rib_width = 5.0
rib_height = 10.0
rib_thickness = bracket_thickness

solid_body = Box(bracket_width, bracket_height, bracket_thickness)

slot_cut = Box(slot_width, slot_height, bracket_thickness)
solid_body = solid_body - slot_cut

notch_cut = Pos(bracket_width/2 - bracket_thickness, bracket_height/2 - notch_offset_from_top - notch_height/2, 0) * Box(bracket_thickness*2, notch_width, notch_height)
solid_body = solid_body - notch_cut

hole_positions = [
    (-bracket_width/2 + hole_offset_x, -bracket_height/2 + hole_offset_y),
    (-bracket_width/2 + hole_offset_x + hole_spacing, -bracket_height/2 + hole_offset_y),
    (-bracket_width/2 + hole_offset_x, -bracket_height/2 + hole_offset_y + hole_spacing)
]
for x, y in hole_positions:
    solid_body = solid_body - Pos(x, y, 0) * Cylinder(hole_diameter/2, bracket_thickness)

rib1 = Pos(-bracket_width/2 + rib_width/2, 0, -rib_thickness/2) * Box(rib_width, rib_height, rib_thickness)
rib2 = Pos(bracket_width/2 - rib_width/2, 0, -rib_thickness/2) * Box(rib_width, rib_height, rib_thickness)
solid_body = solid_body + rib1 + rib2

part = solid_body
part.name = "bracket"
export_step(part, "output.step")