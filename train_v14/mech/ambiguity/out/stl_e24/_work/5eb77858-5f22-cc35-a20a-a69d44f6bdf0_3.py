from build123d import *

panel_width = 80
panel_height = 50
panel_thickness = 5
hole_diameter = 11
hole_spacing = 12
hole_start_offset = 8
fillet_radius = 3
rib_width = 60
rib_height = 5
rib_thickness = 2
slot_width = 20
slot_height = 10
slot_offset_x = -panel_width/2 + 15

with BuildPart() as p:
    with BuildSketch() as s:
        Rectangle(panel_width, panel_height)
    extrude(amount=panel_thickness)

solid_body = p.part
solid_body = fillet(solid_body.edges().filter_by(Axis.Z), fillet_radius)

rib = Pos(0, panel_height/2 - rib_height/2, panel_thickness/2) * Box(rib_width, rib_height, rib_thickness)
solid_body = solid_body + rib

slot = Pos(slot_offset_x, 0, panel_thickness/2) * Box(slot_width, slot_height, panel_thickness + 1)
solid_body = solid_body - slot

for i in range(5):
    x = -panel_width/2 + hole_start_offset + i * hole_spacing
    hole = Pos(x, 0, panel_thickness/2) * Cylinder(hole_diameter/2, panel_thickness + 1)
    solid_body = solid_body - hole

part = solid_body
part.name = "panel_with_rib_slot_holes"
export_step(part, "output.step")