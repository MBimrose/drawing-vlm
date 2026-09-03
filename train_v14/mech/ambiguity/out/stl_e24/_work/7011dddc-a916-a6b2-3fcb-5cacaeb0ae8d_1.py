from build123d import *

chute_length = 80.0
chute_width = 40.0
chute_height = 30.0
wall_thickness = 2.0
v_groove_depth = 10.0
v_groove_width = 15.0
chamfer_distance = 0.5
hole_diameter = 5.0
hole_spacing = 20.0

solid_body = Pos(0, 0, chute_height/2) * Box(chute_length, chute_width, chute_height)
top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[top_face])

with BuildPart() as gp:
    with BuildSketch(Plane.YZ) as sk:
        with BuildLine() as bl:
            Line((-v_groove_width/2, 0), (v_groove_width/2, 0))
            Line((v_groove_width/2, 0), (0, v_groove_depth))
            Line((0, v_groove_depth), (-v_groove_width/2, 0))
        make_face()
    extrude(amount=wall_thickness)
groove = Pos(chute_length/2 - wall_thickness, 0, 0) * gp.part
solid_body = solid_body - groove

for x in [-hole_spacing/2, hole_spacing/2]:
    hole = Pos(x, chute_width/2, chute_height/2) * Rot(90, 0, 0) * Cylinder(hole_diameter/2, chute_width + 10)
    solid_body = solid_body - hole

vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = chamfer(vertical_edges, chamfer_distance)

part = solid_body
part.name = "chute"
export_step(part, "output.step")