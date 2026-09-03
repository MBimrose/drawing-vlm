from build123d import *

horizontal_leg_length = 80.0
vertical_leg_length = 60.0
thickness = 10.0
gusset_thickness = 5.0
hole_diameter = 8.5
hole_spacing = 12.0
hole_edge_clearance = 15.0
chamfer_distance = 1.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0, 0), (horizontal_leg_length, 0), (horizontal_leg_length, thickness),
                     (thickness, thickness), (thickness, vertical_leg_length), (0, vertical_leg_length), close=True)
        make_face()
    extrude(amount=thickness)

with BuildPart() as g:
    with BuildSketch() as gsk:
        with BuildLine() as gbl:
            Polyline((0, 0), (gusset_thickness, 0), (0, gusset_thickness), close=True)
        make_face()
    extrude(amount=thickness)

solid_body = p.part + g.part

for i in range(5):
    x = hole_edge_clearance + i * hole_spacing
    y = thickness / 2
    solid_body = solid_body - Pos(x, y, thickness / 2) * Cylinder(hole_diameter / 2, thickness)

max_x_face = solid_body.faces().sort_by(Axis.X)[-1]
solid_body = chamfer(max_x_face.edges(), chamfer_distance)

part = solid_body
part.name = "L_Bracket"
export_step(part, "output.step")