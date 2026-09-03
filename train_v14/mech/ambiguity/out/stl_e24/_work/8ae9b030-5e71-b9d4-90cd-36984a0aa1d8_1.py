from build123d import *

horizontal_leg_length = 80.0
vertical_leg_length = 60.0
leg_thickness = 8.0
bracket_thickness = 10.0
hole_diameter = 6.0
hole_spacing = 20.0
hole_offset_from_corner = 20.0
chamfer_size = 1.0
gusset = True
pocket_width = 30.0
pocket_depth = 6.0
pocket_offset_from_corner = 15.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0, 0), (horizontal_leg_length, 0), (horizontal_leg_length, leg_thickness),
                     (leg_thickness, leg_thickness), (leg_thickness, vertical_leg_length),
                     (0, vertical_leg_length), close=True)
        make_face()
    extrude(amount=bracket_thickness)

solid_body = p.part

for i in range(3):
    x = hole_offset_from_corner + i * hole_spacing
    y = leg_thickness / 2
    solid_body = solid_body - Pos(x, y, bracket_thickness / 2) * Rot(90, 0, 0) * Cylinder(hole_diameter / 2, bracket_thickness)

pocket = Pos(leg_thickness / 2, pocket_offset_from_corner + pocket_width / 2, bracket_thickness / 2) * Box(leg_thickness, pocket_width, pocket_depth)
solid_body = solid_body - pocket

if gusset:
    with BuildPart() as gp:
        with BuildSketch() as gsk:
            with BuildLine() as gbl:
                Polyline((0, 0), (leg_thickness, 0), (0, leg_thickness), close=True)
            make_face()
        extrude(amount=bracket_thickness)
    solid_body = solid_body + gp.part

vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = chamfer(vertical_edges, chamfer_size)

part = solid_body
part.name = "L_Bracket"
export_step(part, "output.step")