from build123d import *

vertical_leg_length = 70.0
horizontal_leg_length = 60.0
leg_thickness = 8.0
bracket_depth = 20.0
gusset_thickness = 6.0
hole_diameter = 5.0
hole_spacing = 15.0
hole_offset_from_bottom = 10.0
chamfer_size = 0.5

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            l1 = Line((0, 0), (0, vertical_leg_length))
            l2 = Line(l1@1, (leg_thickness, vertical_leg_length))
            l3 = Line(l2@1, (leg_thickness, leg_thickness))
            l4 = Line(l3@1, (horizontal_leg_length, leg_thickness))
            l5 = Line(l4@1, (horizontal_leg_length, 0))
            l6 = Line(l5@1, (0, 0))
        make_face()
    extrude(amount=bracket_depth)

with BuildPart() as g:
    with BuildSketch() as gsk:
        with BuildLine() as gbl:
            gl1 = Line((0, vertical_leg_length), (leg_thickness, vertical_leg_length))
            gl2 = Line(gl1@1, (leg_thickness, vertical_leg_length - gusset_thickness))
            gl3 = Line(gl2@1, (0, vertical_leg_length))
        make_face()
    extrude(amount=bracket_depth)

solid_body = p.part + g.part

for i in range(6):
    x = hole_offset_from_bottom + i * hole_spacing
    solid_body = solid_body - Pos(x, vertical_leg_length, bracket_depth/2) * Rot(90, 0, 0) * Cylinder(hole_diameter/2, 200)

solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_size)

part = solid_body
part.name = "L_Bracket"
export_step(part, "output.step")