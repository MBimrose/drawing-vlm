from build123d import *

leg_length = 80.0
leg_height = 60.0
thickness = 10.0
rib_thickness = 6.0
hole_diameter = 8.5
hole_spacing = 12.0
hole_offset = 15.0
chamfer_distance = 1.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0, 0), (leg_length, 0), (leg_length, thickness), (thickness, thickness), (thickness, leg_height), (0, leg_height), close=True)
        make_face()
    extrude(amount=thickness)

solid_body = p.part

with BuildPart() as rib_p:
    with BuildSketch() as rib_sk:
        with BuildLine() as rib_bl:
            Polyline((0, 0), (rib_thickness, 0), (0, rib_thickness), close=True)
        make_face()
    extrude(amount=thickness)

solid_body = solid_body + rib_p.part

for i in range(5):
    x = hole_offset + i * hole_spacing
    y = thickness / 2
    solid_body = solid_body - Pos(x, y, thickness / 2) * Cylinder(hole_diameter / 2, thickness)

right_face = solid_body.faces().sort_by(Axis.X)[-1]
right_edges = right_face.edges()
solid_body = chamfer(right_edges, chamfer_distance)

part = solid_body
part.name = "L_Bracket"
export_step(part, "output.step")