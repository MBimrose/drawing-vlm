from build123d import *

vertical_leg_height = 70.0
horizontal_leg_length = 80.0
leg_width = 20.0
bracket_thickness = 8.0
gusset_length = 30.0
gusset_thickness = 5.0
hole_diameter = 5.0
hole_spacing = 20.0
hole_rows = 2
hole_columns = 1
chamfer_distance = 1.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0,0), (0, vertical_leg_height), (leg_width, vertical_leg_height),
                     (leg_width, leg_width), (horizontal_leg_length, leg_width),
                     (horizontal_leg_length, 0), close=True)
        make_face()
    extrude(amount=bracket_thickness)
base = p.part

with BuildPart() as g:
    with BuildSketch() as gsk:
        with BuildLine() as gbl:
            Polyline((leg_width, leg_width), (leg_width + gusset_length, leg_width),
                     (leg_width, leg_width + gusset_length), close=True)
        make_face()
    extrude(amount=gusset_thickness)
gusset = g.part

solid_body = base + gusset

for i in range(hole_rows):
    for j in range(hole_columns):
        x = leg_width / 2 + (i - (hole_rows - 1) / 2) * hole_spacing
        y = vertical_leg_height / 2 + (j - (hole_columns - 1) / 2) * hole_spacing
        solid_body = solid_body - Pos(x, y, bracket_thickness / 2) * Cylinder(hole_diameter / 2, bracket_thickness + 1)

min_x_face = solid_body.faces().sort_by(Axis.X)[0]
solid_body = chamfer(min_x_face.edges(), chamfer_distance)

part = solid_body
part.name = "L_Bracket"
export_step(part, "output.step")