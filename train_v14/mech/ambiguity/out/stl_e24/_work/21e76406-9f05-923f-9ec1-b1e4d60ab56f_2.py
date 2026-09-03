from build123d import *

leg_length_vertical = 70.0
leg_length_horizontal = 80.0
bracket_thickness = 6.0
gusset_thickness = 4.0
gusset_base = 12.0
gusset_height = 40.0
hole_diameter = 5.0
cbore_diameter = 7.5
cbore_depth = 2.0
hole_spacing = 25.0
hole_offset = 10.0
fillet_radius = 2.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0, 0), (leg_length_horizontal, 0), (leg_length_horizontal, bracket_thickness),
                     (bracket_thickness, bracket_thickness), (bracket_thickness, leg_length_vertical),
                     (0, leg_length_vertical), close=True)
        make_face()
    extrude(amount=bracket_thickness)

solid_body = p.part
solid_body = fillet(solid_body.edges().filter_by(Axis.Z), fillet_radius)

with BuildPart() as g:
    with BuildSketch(Plane.YZ.offset(bracket_thickness)) as sk:
        with BuildLine() as bl:
            Polyline((bracket_thickness, 0), (bracket_thickness + gusset_base, 0),
                     (bracket_thickness + gusset_thickness, gusset_height), close=True)
        make_face()
    extrude(amount=-gusset_thickness)

solid_body = solid_body + g.part

for i in range(2):
    x = hole_offset + i * hole_spacing
    y = bracket_thickness / 2
    solid_body = solid_body - Pos(x, y, bracket_thickness - cbore_depth/2) * Cylinder(cbore_diameter/2, cbore_depth)
    solid_body = solid_body - Pos(x, y, bracket_thickness/2) * Cylinder(hole_diameter/2, bracket_thickness + 10)

for i in range(2):
    x = bracket_thickness / 2
    y = hole_offset + i * hole_spacing
    solid_body = solid_body - Pos(x, y, bracket_thickness - cbore_depth/2) * Cylinder(cbore_diameter/2, cbore_depth)
    solid_body = solid_body - Pos(x, y, bracket_thickness/2) * Cylinder(hole_diameter/2, bracket_thickness + 10)

part = solid_body
part.name = "L_bracket_with_gusset"
export_step(part, "output.step")