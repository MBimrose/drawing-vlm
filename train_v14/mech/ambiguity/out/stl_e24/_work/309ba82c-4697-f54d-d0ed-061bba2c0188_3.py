from build123d import *

chute_length = 90.0
chute_width = 40.0
chute_height = 30.0
wall_thickness = 3.0
v_groove_width = 12.0
v_groove_depth = 8.0
fillet_radius = 2.0
mount_hole_diameter = 5.0
mount_hole_offset = 15.0

base = Pos(0, 0, chute_height/2) * Box(chute_length, chute_width, chute_height)
top_face = base.faces().sort_by(Axis.Z)[-1]
base = offset(base, amount=-wall_thickness, openings=[top_face])

with BuildPart() as gp:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            l1 = Line((0, 0), (v_groove_width/2, v_groove_depth))
            l2 = Line(l1@1, (-v_groove_width/2, v_groove_depth))
            l3 = Line(l2@1, (0, 0))
        make_face()
    extrude(amount=chute_length)
groove = Pos(0, chute_width/2, chute_height/2) * gp.part
base = base - groove

hole = Pos(-chute_length/2 + mount_hole_offset, -chute_width/2 + wall_thickness/2, chute_height) * Rot(90, 0, 0) * Cylinder(mount_hole_diameter/2, wall_thickness + 1)
base = base - hole

bottom_edges = base.faces().sort_by(Axis.Z)[0].edges()
base = fillet(bottom_edges, fillet_radius)

part = base
part.name = "chute"
export_step(part, "output.step")