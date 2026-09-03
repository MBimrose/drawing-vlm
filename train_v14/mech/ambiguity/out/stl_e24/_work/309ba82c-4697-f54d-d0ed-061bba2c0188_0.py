from build123d import *

chute_length = 90.0
chute_width = 40.0
chute_height = 30.0
wall_thickness = 3.0
v_groove_depth = 12.0
v_groove_width = 20.0
fillet_radius = 2.0
hole_diameter = 5.0
hole_offset_from_end = 20.0

base = Pos(0, 0, chute_height/2) * Box(chute_length, chute_width, chute_height)
top_face = base.faces().sort_by(Axis.Z)[-1]
base = offset(base, amount=-wall_thickness, openings=[top_face])

with BuildPart() as gp:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            l1 = Line((0, 0), (v_groove_depth, v_groove_width/2))
            l2 = Line(l1@1, (v_groove_depth, -v_groove_width/2))
            l3 = Line(l2@1, (0, 0))
        make_face()
    extrude(amount=chute_length)
groove = Pos(0, chute_width/2 - wall_thickness, chute_height/2) * gp.part

result = base - groove

bottom_face = result.faces().sort_by(Axis.Z)[0]
result = fillet(bottom_face.edges(), fillet_radius)

hole = Pos(-chute_length/2 + hole_offset_from_end, -chute_width/2 + wall_thickness/2, chute_height) * Rot(90, 0, 0) * Cylinder(hole_diameter/2, chute_width)
result = result - hole

part = result
part.name = "chute"
export_step(part, "output.step")