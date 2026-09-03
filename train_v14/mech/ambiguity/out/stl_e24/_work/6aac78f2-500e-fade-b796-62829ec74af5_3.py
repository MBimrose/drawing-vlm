from build123d import *

bracket_width = 80.0
bracket_height = 60.0
bracket_thickness = 10.0
wall_thickness = 1.0
notch_width = 20.0
notch_depth = 5.0
pocket_width = 30.0
pocket_height = 20.0
pocket_depth = 6.0
hole_diameter = 4.0
cbore_diameter = 6.0
cbore_depth = 2.0
hole_spacing = 20.0
chamfer_size = 2.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            l1 = Line((-bracket_width/2, -bracket_height/2), (bracket_width/2, -bracket_height/2))
            l2 = Line(l1@1, (bracket_width/2, bracket_height/2 - notch_depth))
            l3 = Line(l2@1, (bracket_width/2 - notch_width, bracket_height/2 - notch_depth))
            l4 = Line(l3@1, (bracket_width/2 - notch_width, bracket_height/2))
            l5 = Line(l4@1, (-bracket_width/2, bracket_height/2))
            l6 = Line(l5@1, (-bracket_width/2, -bracket_height/2))
        make_face()
    extrude(amount=bracket_thickness)

solid_body = p.part
solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_size)
solid_body = offset(solid_body, amount=-wall_thickness)

pocket = Pos(bracket_width/2 - pocket_depth/2, 0, bracket_thickness/2) * Box(pocket_depth, pocket_width, pocket_height)
solid_body = solid_body - pocket

for y in [-hole_spacing/2, hole_spacing/2]:
    shaft = Pos(0, y, bracket_thickness/2) * Rot(0, 90, 0) * Cylinder(hole_diameter/2, bracket_width + 10)
    solid_body = solid_body - shaft
    cbore = Pos(bracket_width/2 - cbore_depth/2, y, bracket_thickness/2) * Rot(0, 90, 0) * Cylinder(cbore_diameter/2, cbore_depth)
    solid_body = solid_body - cbore

part = solid_body
part.name = "bracket"
export_step(part, "output.step")