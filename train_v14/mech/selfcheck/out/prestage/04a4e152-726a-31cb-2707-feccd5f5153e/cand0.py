from build123d import *

leg_length = 50.0
leg_height = 30.0
leg_thickness = 10.0
bracket_thickness = 12.0
pocket_width = 6.0
pocket_height = 8.0
pocket_depth = 6.0
pocket_offset = 20.0
hole_diameter = 6.0
hole_depth = 8.0
hole_offset = 5.0
chamfer_size = 1.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0, 0), (leg_length, 0), (leg_length, leg_thickness),
                     (leg_thickness, leg_thickness), (leg_thickness, leg_height),
                     (0, leg_height), close=True)
        make_face()
    extrude(amount=bracket_thickness)

solid_body = p.part

pocket1 = Pos(pocket_offset + pocket_width/2, leg_thickness/2, bracket_thickness - pocket_depth/2) * Box(pocket_width, pocket_height, pocket_depth)
solid_body = solid_body - pocket1

pocket2 = Pos(leg_thickness/2, pocket_offset + pocket_height/2, bracket_thickness - pocket_depth/2) * Box(pocket_width, pocket_height, pocket_depth)
solid_body = solid_body - pocket2

hole = Pos(leg_thickness/2, leg_height - hole_offset, hole_depth/2) * Cylinder(hole_diameter/2, hole_depth)
solid_body = solid_body - hole

vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = chamfer(vertical_edges, chamfer_size)

part = solid_body
part.name = "L_bracket"
export_step(part, "output.step")