from build123d import *

bracket_length = 80
bracket_width = 40
bracket_thickness = 8
rib_height = 4
rib_width = 60
rib_thickness = 4
slot_length = 15
slot_width = 3
slot_spacing = 20
slot_offset_y = 12
fillet_radius = 2
chamfer_distance = 0.5
hole_diameter = 6

with BuildPart() as p:
    with BuildSketch() as s:
        Rectangle(bracket_length, bracket_width)
    extrude(amount=bracket_thickness)

solid_body = p.part
solid_body = fillet(solid_body.edges().filter_by(Axis.Z), fillet_radius)

rib = Pos(0, -bracket_width/2 - rib_thickness/2, bracket_thickness/2) * Box(rib_width, rib_thickness, rib_height)
solid_body = solid_body + rib

for x, y in [(-slot_spacing, slot_offset_y), (0, slot_offset_y), (slot_spacing, slot_offset_y)]:
    slot = Pos(x, y, bracket_thickness/2) * Box(slot_length, slot_width, bracket_thickness)
    solid_body = solid_body - slot

solid_body = solid_body - Pos(0, 0, bracket_thickness/2) * Cylinder(hole_diameter/2, bracket_thickness)

solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_distance)

part = solid_body
part.name = "bracket_with_rib_and_slots"
export_step(part, "output.step")