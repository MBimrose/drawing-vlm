from build123d import *

vertical_leg_length = 70.0
horizontal_leg_length = 80.0
leg_width = 20.0
thickness = 8.0
gusset_thickness = 5.0
gusset_height = 30.0
hole_diameter = 4.0
hole_spacing = 15.0
hole_count = 3
chamfer_distance = 1.0

with BuildPart() as p:
    with BuildSketch() as s:
        with BuildLine() as l:
            Polyline((0,0), (0, vertical_leg_length), (leg_width, vertical_leg_length),
                     (leg_width, leg_width), (horizontal_leg_length, leg_width),
                     (horizontal_leg_length, 0), close=True)
        make_face()
    extrude(amount=thickness)
base = p.part

with BuildPart() as g:
    with BuildSketch() as s:
        with BuildLine() as l:
            Polyline((leg_width, leg_width), (leg_width, leg_width + gusset_height),
                     (leg_width + gusset_height, leg_width), close=True)
        make_face()
    extrude(amount=gusset_thickness)
gusset = g.part

solid_body = base + gusset

for i in range(hole_count):
    y = leg_width + hole_spacing + i * hole_spacing
    solid_body = solid_body - Pos(leg_width/2, y, 0) * Cylinder(hole_diameter/2, thickness + 2)

x_face = solid_body.faces().sort_by(Axis.X)[0]
solid_body = chamfer(x_face.edges(), chamfer_distance)

part = solid_body
part.name = "L_Bracket"
export_step(part, "output.step")