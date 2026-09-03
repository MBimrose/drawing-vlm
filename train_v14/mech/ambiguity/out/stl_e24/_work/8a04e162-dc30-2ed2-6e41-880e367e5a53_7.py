from build123d import *

bracket_length = 80.0
bracket_width = 40.0
bracket_thickness = 8.0
rib_height = 4.0
rib_width = 70.0
hole_diameter = 6.0
slot_length = 15.0
slot_width = 3.0
slot_spacing = 20.0
num_slots = 3
fillet_radius = 2.0
chamfer_distance = 0.5

with BuildPart() as p:
    with BuildSketch() as s:
        Rectangle(bracket_length, bracket_width)
    extrude(amount=bracket_thickness)

solid_body = p.part
solid_body = fillet(solid_body.edges().filter_by(Axis.Z), fillet_radius)

rib = Pos(0, -bracket_width/2 - rib_height/2, bracket_thickness/2) * Box(rib_width, rib_height, rib_height)
solid_body = solid_body + rib

solid_body = solid_body - Pos(0, 0, bracket_thickness/2) * Cylinder(hole_diameter/2, bracket_thickness * 2)

for i in range(num_slots):
    x = (i - (num_slots - 1) / 2) * slot_spacing
    slot = Pos(x, bracket_width/2 - slot_width/2 - 2, bracket_thickness/2) * Box(slot_length, slot_width, bracket_thickness * 2)
    solid_body = solid_body - slot

solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_distance)

part = solid_body
part.name = "bracket"
export_step(part, "output.step")