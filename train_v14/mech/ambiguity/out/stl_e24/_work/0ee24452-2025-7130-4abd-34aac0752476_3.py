from build123d import *

leg_length_vertical = 70.0
leg_length_horizontal = 60.0
thickness = 8.0
width = 20.0
notch_width = 6.0
notch_depth = 4.0
hole_diameter = 5.0
hole_offset = 10.0
chamfer_size = 0.8

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0, 0), (0, leg_length_vertical), (thickness, leg_length_vertical),
                     (thickness, thickness), (leg_length_horizontal, thickness),
                     (leg_length_horizontal, 0), close=True)
        make_face()
    extrude(amount=width)

solid_body = p.part

with BuildPart() as notch_p:
    with BuildSketch() as ns:
        with BuildLine() as nbl:
            Polyline((0, leg_length_vertical), (notch_width, leg_length_vertical),
                     (0, leg_length_vertical - notch_depth), close=True)
        make_face()
    extrude(amount=width)

solid_body = solid_body - notch_p.part

solid_body = solid_body - Pos(hole_offset, leg_length_vertical/2, width/2) * Rot(90, 0, 0) * Cylinder(hole_diameter/2, leg_length_vertical + 10)
solid_body = solid_body - Pos(leg_length_horizontal/2, hole_offset, width/2) * Rot(0, 90, 0) * Cylinder(hole_diameter/2, leg_length_horizontal + 10)

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
top_edges = top_face.edges()
solid_body = chamfer(top_edges, chamfer_size)

part = solid_body
part.name = "L_Bracket"
export_step(part, "output.step")