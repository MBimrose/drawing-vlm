from build123d import *

leg_length_long = 80.0
leg_length_short = 60.0
leg_thickness = 10.0
bracket_depth = 8.0
gusset_depth = 4.0
hole_diameter = 4.0
hole_spacing = 15.0
hole_count = 3
chamfer_size = 1.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0, 0), (leg_length_short, 0), (leg_length_short, leg_thickness),
                     (leg_thickness, leg_thickness), (leg_thickness, leg_length_long),
                     (0, leg_length_long), close=True)
        make_face()
    extrude(amount=bracket_depth)

solid_body = p.part

with BuildPart() as g:
    with BuildSketch(Plane.XY.offset(bracket_depth)) as gsk:
        with BuildLine() as gbl:
            Polyline((leg_thickness, leg_thickness), (leg_thickness + leg_thickness, leg_thickness),
                     (leg_thickness, leg_thickness + leg_thickness), close=True)
        make_face()
    extrude(amount=gusset_depth)

solid_body = solid_body + g.part

for i in range(hole_count):
    x = leg_length_short / 2 + (i - (hole_count - 1) / 2) * hole_spacing
    y = leg_thickness / 2
    solid_body = solid_body - Pos(x, y, bracket_depth + gusset_depth) * Cylinder(hole_diameter / 2, bracket_depth + gusset_depth + 10)

solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_size)

part = solid_body
part.name = "L_bracket_with_gusset"
export_step(part, "output.step")