from build123d import *

vertical_leg_length = 70.0
horizontal_leg_length = 80.0
bracket_thickness = 6.0
gusset_thickness = 6.0
gusset_height = 48.0
hole_diameter = 5.0
cbore_diameter = 7.5
cbore_depth = 2.0
fillet_radius = 2.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0, 0), (0, vertical_leg_length), (bracket_thickness, vertical_leg_length),
                     (bracket_thickness, bracket_thickness), (horizontal_leg_length, bracket_thickness),
                     (horizontal_leg_length, 0), close=True)
        make_face()
    extrude(amount=bracket_thickness)

solid_body = p.part

with BuildPart() as g:
    with BuildSketch(Plane.YZ) as gsk:
        with BuildLine() as gbl:
            Polyline((bracket_thickness, 0), (bracket_thickness, gusset_height),
                     (bracket_thickness + gusset_thickness, 0), close=True)
        make_face()
    extrude(amount=gusset_thickness)

solid_body = solid_body + g.part

hole_positions = [
    (horizontal_leg_length * 0.33, bracket_thickness / 2),
    (horizontal_leg_length * 0.66, bracket_thickness / 2),
    (bracket_thickness / 2, vertical_leg_length * 0.33),
]

for x, y in hole_positions:
    solid_body = solid_body - Pos(x, y, bracket_thickness - cbore_depth/2) * Cylinder(cbore_diameter/2, cbore_depth)
    solid_body = solid_body - Pos(x, y, bracket_thickness/2) * Cylinder(hole_diameter/2, bracket_thickness + 10)

solid_body = fillet(solid_body.edges().filter_by(Axis.Z), fillet_radius)

part = solid_body
part.name = "L_Bracket"
export_step(part, "output.step")