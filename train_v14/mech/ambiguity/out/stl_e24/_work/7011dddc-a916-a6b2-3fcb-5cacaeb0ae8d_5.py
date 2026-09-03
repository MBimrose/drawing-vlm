from build123d import *

chute_length = 80.0
chute_width = 40.0
chute_height = 30.0
wall_thickness = 2.0
notch_depth = 8.0
notch_width = 15.0
chamfer_size = 0.5
hole_diameter = 5.0
hole_spacing = 20.0

base = Pos(0, 0, chute_height/2) * Box(chute_length, chute_width, chute_height)

with BuildPart() as notch_bp:
    with BuildSketch(Plane.YZ.offset(chute_length/2)) as notch_sk:
        with BuildLine() as notch_line:
            Polyline((-notch_width/2, 0), (notch_width/2, 0), (0, notch_depth), close=True)
        make_face()
    extrude(amount=-notch_depth)

solid_body = base - notch_bp.part

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[top_face])

vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = chamfer(vertical_edges, chamfer_size)

for x in [-hole_spacing/2, hole_spacing/2]:
    hole = Pos(x, chute_width/2, chute_height/2) * Rot(90, 0, 0) * Cylinder(hole_diameter/2, chute_width + 10)
    solid_body = solid_body - hole

part = solid_body
part.name = "chute"
export_step(part, "output.step")