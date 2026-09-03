from build123d import *

bracket_length = 80.0
bracket_width = 40.0
bracket_thickness = 5.0
slot_width = 20.0
slot_length = 30.0
slot_radius = 10.0
hole_diameter = 10.0
hole_offset = 10.0
rib_width = 5.0
rib_height = 3.0
chamfer_size = 1.0
relief_depth = 2.0
relief_width = 5.0

with BuildPart() as p:
    with BuildSketch() as s:
        Rectangle(bracket_length, bracket_width)
    extrude(amount=bracket_thickness)

solid_body = p.part
solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_size)

with BuildPart() as slot_p:
    with BuildSketch() as slot_sk:
        SlotOverall(slot_length, slot_width)
    extrude(amount=bracket_thickness)
solid_body = solid_body - slot_p.part

hole_positions = [(-bracket_length/2 + hole_offset, 0), (bracket_length/2 - hole_offset, 0)]
for x, y in hole_positions:
    solid_body = solid_body - Pos(x, y, bracket_thickness/2) * Cylinder(hole_diameter/2, bracket_thickness)

rib = Pos(0, 0, bracket_thickness/2 + rib_height/2) * Box(rib_width, bracket_width - 2*hole_offset, rib_height)
solid_body = solid_body + rib

for x, y in hole_positions:
    relief = Pos(x, y, bracket_thickness/4) * Box(relief_width, relief_width, bracket_thickness/2)
    solid_body = solid_body - relief

part = solid_body
part.name = "bracket"
export_step(part, "output.step")