from build123d import *

leg_length_long = 80.0
leg_length_short = 50.0
leg_width = 20.0
bracket_thickness = 8.0
gusset_length = 30.0
gusset_thickness = 5.0
hole_diameter = 5.0
hole_spacing = 20.0
chamfer_size = 1.0

with BuildPart() as p:
    with BuildSketch() as s:
        with BuildLine() as l:
            Polyline((0,0), (leg_length_long, 0), (leg_length_long, leg_width),
                     (leg_width, leg_width), (leg_width, leg_width + leg_length_short),
                     (0, leg_width + leg_length_short), close=True)
        make_face()
    extrude(amount=bracket_thickness)
base = p.part

with BuildPart() as g:
    with BuildSketch() as s:
        with BuildLine() as l:
            Polyline((leg_width, leg_width), (leg_width + gusset_length, leg_width),
                     (leg_width, leg_width + gusset_length), close=True)
        make_face()
    extrude(amount=gusset_thickness)
gusset = g.part

solid_body = base + gusset

hole_r = hole_diameter / 2
hole_h = bracket_thickness + 2
for x, y in [(leg_width + hole_spacing, leg_width/2), (leg_width + 2*hole_spacing, leg_width/2),
             (leg_width/2, leg_width + hole_spacing), (leg_width/2, leg_width + 2*hole_spacing)]:
    solid_body = solid_body - Pos(x, y, bracket_thickness/2) * Cylinder(hole_r, hole_h)

back_face = solid_body.faces().sort_by(Axis.X)[0]
solid_body = chamfer(back_face.edges(), chamfer_size)

part = solid_body
part.name = "L_Bracket"
export_step(part, "output.step")