from build123d import *

horizontal_length = 80.0
vertical_length = 60.0
thickness = 8.0
leg_width = 12.0
rib_width = 8.0
rib_height = 6.0
rib_thickness = 4.0
hole_diameter = 4.5
hole_spacing = 20.0
hole_offset = 10.0
fillet_radius = 2.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0, 0), (horizontal_length, 0), (horizontal_length, vertical_length + thickness),
                     (horizontal_length - leg_width, vertical_length + thickness),
                     (horizontal_length - leg_width, thickness), (0, thickness), close=True)
        make_face()
    extrude(amount=thickness)

solid_body = p.part

rib = Pos(leg_width/2, thickness/2, thickness + rib_thickness/2) * Box(rib_width, rib_height, rib_thickness)
solid_body = solid_body + rib

pocket = Pos(horizontal_length - leg_width/2, thickness + vertical_length/2, thickness - rib_thickness/2) * Box(leg_width/2, vertical_length/3, rib_thickness)
solid_body = solid_body - pocket

for i in range(3):
    y_pos = thickness + hole_offset + i * hole_spacing
    hole = Pos(horizontal_length - leg_width/2, y_pos, thickness/2) * Cylinder(hole_diameter/2, thickness)
    solid_body = solid_body - hole

inner_edges = [e for e in solid_body.edges().filter_by(Axis.Z) if abs(e.center().X) < 1e-6 and abs(e.center().Y) < 1e-6]
solid_body = fillet(inner_edges, fillet_radius)

part = solid_body
part.name = "L_Bracket"
export_step(part, "output.step")