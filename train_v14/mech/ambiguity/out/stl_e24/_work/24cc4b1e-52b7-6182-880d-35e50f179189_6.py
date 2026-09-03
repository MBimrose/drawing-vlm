from build123d import *

horizontal_length = 80.0
vertical_length = 70.0
leg_width = 20.0
thickness = 8.0
fillet_radius = 2.0
hole_diameter = 4.0
hole_count = 4
hole_margin = 10.0
counterbore_diameter = 6.0
counterbore_depth = 4.0
counterbore_outer = 10.0
gusset_width = 15.0
gusset_height = 15.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            l1 = Line((0, 0), (horizontal_length, 0))
            l2 = Line(l1@1, (horizontal_length, leg_width))
            l3 = Line(l2@1, (leg_width, leg_width))
            l4 = Line(l3@1, (leg_width, vertical_length))
            l5 = Line(l4@1, (0, vertical_length))
            l6 = Line(l5@1, (0, 0))
        make_face()
    extrude(amount=thickness)

solid_body = p.part
solid_body = fillet(solid_body.edges(), fillet_radius)

hole_spacing = (horizontal_length - 2 * hole_margin) / (hole_count + 1)
for i in range(hole_count):
    x = hole_margin + hole_spacing * (i + 1)
    y = leg_width / 2
    solid_body = solid_body - Pos(x, y, thickness/2) * Cylinder(hole_diameter/2, thickness + 1)

cb_y = vertical_length / 2
cb_z = thickness / 2
solid_body = solid_body - Pos(counterbore_depth/2, cb_y, cb_z) * Rot(0, 90, 0) * Cylinder(counterbore_outer/2, counterbore_depth)
solid_body = solid_body - Pos(thickness/2, cb_y, cb_z) * Rot(0, 90, 0) * Cylinder(counterbore_diameter/2, thickness + 1)

with BuildPart() as g:
    with BuildSketch() as gs:
        with BuildLine() as gl:
            gl1 = Line((0, 0), (gusset_width, 0))
            gl2 = Line(gl1@1, (0, gusset_height))
            gl3 = Line(gl2@1, (0, 0))
        make_face()
    extrude(amount=thickness)

solid_body = solid_body + g.part

part = solid_body
part.name = "L_Bracket"
export_step(part, "output.step")