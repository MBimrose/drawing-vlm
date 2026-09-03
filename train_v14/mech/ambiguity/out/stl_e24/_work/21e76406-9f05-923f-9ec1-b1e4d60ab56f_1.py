from build123d import *

leg_length = 80.0
leg_height = 70.0
thickness = 6.0
fillet_radius = 2.0
gusset_thickness = 3.0
gusset_height = leg_height * 0.8
hole_diameter = 5.0
cbore_diameter = 7.5
cbore_depth = 2.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            l1 = Line((0, 0), (leg_length, 0))
            l2 = Line(l1 @ 1, (leg_length, thickness))
            l3 = Line(l2 @ 1, (thickness, thickness))
            l4 = Line(l3 @ 1, (thickness, leg_height))
            l5 = Line(l4 @ 1, (0, leg_height))
            l6 = Line(l5 @ 1, (0, 0))
        make_face()
    extrude(amount=thickness)

solid_body = p.part
solid_body = fillet(solid_body.edges().filter_by(Axis.Z), fillet_radius)

with BuildPart() as g:
    with BuildSketch(Plane.YZ.offset(thickness)) as gsk:
        with BuildLine() as gbl:
            gl1 = Line((0, 0), (gusset_thickness, 0))
            gl2 = Line(gl1 @ 1, (0, gusset_height))
            gl3 = Line(gl2 @ 1, (0, 0))
        make_face()
    extrude(amount=thickness)

solid_body = solid_body + g.part

hole_r = hole_diameter / 2
cbore_r = cbore_diameter / 2
hole_tool = Cylinder(hole_r, thickness * 2)
cbore_tool = Cylinder(cbore_r, cbore_depth)

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
tc = top_face.center()

for dx, dy in [(leg_length * 0.33, thickness / 2),
               (leg_length * 0.66, thickness / 2),
               (thickness / 2, leg_height * 0.33),
               (thickness / 2, leg_height * 0.66)]:
    px, py, pz = tc.X + dx, tc.Y + dy, tc.Z
    solid_body = solid_body - Pos(px, py, pz) * hole_tool
    solid_body = solid_body - Pos(px, py, pz - cbore_depth / 2) * cbore_tool

part = solid_body
part.name = "L_Bracket"
export_step(part, "output.step")