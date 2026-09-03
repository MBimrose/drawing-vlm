from build123d import *

chute_length = 90.0
chute_width = 40.0
chute_height = 30.0
wall_thickness = 3.0
v_depth = 10.0
fillet_radius = 2.0
mount_hole_dia = 5.0
mount_hole_offset = 20.0

base = Pos(0, 0, chute_height/2) * Box(chute_length, chute_width, chute_height)
top_face = base.faces().sort_by(Axis.Z)[-1]
base = offset(base, amount=-wall_thickness, openings=[top_face])

with BuildPart() as v_bp:
    with BuildSketch(Plane.XZ.offset(-chute_width/2)) as v_sk:
        with BuildLine() as v_line:
            Polyline((0, chute_height/2 - v_depth/2), (v_depth, chute_height/2), (0, chute_height/2 + v_depth/2), close=True)
        make_face()
    extrude(amount=chute_length - 2*wall_thickness)
v_cut = v_bp.part

result = base - v_cut

hole = Pos(-chute_length/2 + mount_hole_offset, -chute_width/2, chute_height) * Rot(90, 0, 0) * Cylinder(mount_hole_dia/2, chute_width + 10)
result = result - hole

bottom_face = result.faces().sort_by(Axis.Z)[0]
bottom_edges = bottom_face.edges()
result = fillet(bottom_edges, fillet_radius)

part = result
part.name = "chute"
export_step(part, "output.step")