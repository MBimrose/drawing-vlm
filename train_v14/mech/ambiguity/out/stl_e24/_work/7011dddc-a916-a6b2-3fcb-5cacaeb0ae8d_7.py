from build123d import *

chute_length = 80.0
chute_width = 40.0
chute_height = 30.0
wall_thickness = 2.0
v_groove_width = 12.0
v_groove_depth = 8.0
fillet_radius = 0.5
hole_diameter = 5.0
hole_spacing = 20.0
hole_offset_from_bottom = 10.0

base = Pos(0, 0, chute_height/2) * Box(chute_length, chute_width, chute_height)
top_face = base.faces().sort_by(Axis.Z)[-1]
base = offset(base, amount=-wall_thickness, openings=[top_face])

with BuildPart() as gp:
    with BuildSketch(Plane.YZ) as sk:
        with BuildLine() as bl:
            l1 = Line((-v_groove_width/2, 0), (0, v_groove_depth))
            l2 = Line(l1@1, (v_groove_width/2, 0))
            l3 = Line(l2@1, (-v_groove_width/2, 0))
        make_face()
    extrude(amount=chute_length)
groove = Pos(-chute_length/2, 0, wall_thickness) * gp.part
base = base - groove

hole_r = hole_diameter / 2
hole_h = chute_width + 20
for x in [-hole_spacing/2, hole_spacing/2]:
    base = base - Pos(x, chute_width/2, chute_height/2) * Rot(90, 0, 0) * Cylinder(hole_r, hole_h)

base = fillet(base.edges().filter_by(Axis.Z), fillet_radius)

part = base
part.name = "chute"
export_step(part, "output.step")