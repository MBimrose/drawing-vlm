from build123d import *

leg_length = 60.0
leg_width = 20.0
thickness = 10.0
rib_thickness = 2.0
rib_width = 4.0
rib_height = leg_width
hole_diameter = 4.0
hole_offset = 30.0
pocket_width = 12.0
pocket_depth = 6.0
chamfer_size = 0.8

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0, 0), (leg_length, 0), (leg_length, leg_width),
                     (leg_width, leg_width), (leg_width, leg_length),
                     (0, leg_length), close=True)
        make_face()
    extrude(amount=thickness)

solid_body = p.part

rib1 = Pos(leg_length + rib_thickness/2, leg_width/2, thickness/2) * Box(rib_thickness, rib_width, rib_height)
solid_body = solid_body + rib1

rib2 = Pos(leg_width/2, leg_length + rib_thickness/2, thickness/2) * Box(rib_width, rib_thickness, rib_height)
solid_body = solid_body + rib2

hole = Pos(leg_length, leg_width/2, thickness/2) * Rot(0, 90, 0) * Cylinder(hole_diameter/2, 200)
solid_body = solid_body - hole

pocket = Pos(leg_width/2, leg_width/2, thickness) * Box(pocket_width, pocket_width, pocket_depth)
solid_body = solid_body - pocket

vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = chamfer(vertical_edges, chamfer_size)

part = solid_body
part.name = "L_bracket_with_ribs"
export_step(part, "output.step")