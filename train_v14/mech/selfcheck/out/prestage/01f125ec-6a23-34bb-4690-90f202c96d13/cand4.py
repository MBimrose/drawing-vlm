from build123d import *

base_length = 80.0
vertical_height = 70.0
leg_width = 30.0
thickness = 8.0
fillet_radius = 4.0
hole_diameter = 6.0
hole_spacing = 30.0
slot_width = 15.0
slot_height = 8.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0, 0), (base_length, 0), (base_length, leg_width),
                     (leg_width, leg_width), (leg_width, vertical_height),
                     (0, vertical_height), close=True)
        make_face()
    extrude(amount=thickness)

solid_body = p.part

inner_edge = solid_body.edges().filter_by(Axis.Z).sort_by(Axis.X)[2]
solid_body = fillet([inner_edge], fillet_radius)

slot = Pos(leg_width/2, vertical_height/2, thickness/2) * Box(slot_width, slot_height, thickness)
solid_body = solid_body - slot

for i in range(3):
    x = base_length/2 + (i - 1) * hole_spacing
    y = leg_width/2
    solid_body = solid_body - Pos(x, y, thickness/2) * Cylinder(hole_diameter/2, thickness)

for i in range(3):
    x = leg_width/2
    y = vertical_height/2 + (i - 1) * hole_spacing
    solid_body = solid_body - Pos(x, y, thickness/2) * Cylinder(hole_diameter/2, thickness)

part = solid_body
part.name = "L_Bracket"
export_step(part, "output.step")