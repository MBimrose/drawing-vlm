from build123d import *

leg_length = 80.0
leg_height = 70.0
leg_width = 12.0
thickness = 8.0
rib_width = 8.0
rib_height = 6.0
rib_offset = 5.0
pocket_width = 6.0
pocket_height = 20.0
pocket_depth = 4.0
pocket_offset = 20.0
hole_diameter = 4.5
hole_spacing = 10.0
hole_start_offset = 20.0
fillet_radius = 2.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0, 0), (leg_length, 0), (leg_length, leg_height),
                     (leg_length - leg_width, leg_height),
                     (leg_length - leg_width, leg_width), (0, leg_width), close=True)
        make_face()
    extrude(amount=thickness)

solid_body = p.part
rib = Pos(rib_offset, rib_height/2, thickness + thickness/4) * Box(rib_width, rib_height, thickness/2)
solid_body = solid_body + rib
pocket = Pos(leg_length - leg_width/2, pocket_offset + pocket_height/2, thickness - pocket_depth/2) * Box(pocket_width, pocket_height, pocket_depth)
solid_body = solid_body - pocket

for i in range(3):
    y_pos = hole_start_offset + i * hole_spacing
    hole = Pos(leg_length - leg_width/2, y_pos, thickness/2) * Cylinder(hole_diameter/2, thickness)
    solid_body = solid_body - hole

inner_edges = solid_body.edges().filter_by(Axis.Z).sort_by(Axis.X)[1:2]
solid_body = fillet(inner_edges, fillet_radius)

part = solid_body
part.name = "L_bracket"
export_step(part, "output.step")