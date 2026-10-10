from build123d import *

leg_length_horizontal = 80.0
leg_length_vertical = 70.0
bracket_thickness = 6.0
gusset_base = 20.0
gusset_height = 40.0
gusset_thickness = 4.0
hole_diameter = 5.0
hole_clearance = 5.0
hole_cbore_diameter = 7.5
hole_cbore_depth = 2.0
hole_spacing = 20.0
hole_offset_from_corner = 15.0
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

with BuildPart() as g:
    with BuildSketch(Plane.YZ) as gsk:
        with BuildLine() as gbl:
            Polyline((0, 0), (gusset_base, 0), (0, gusset_height), close=True)
        make_face()
    extrude(amount=gusset_thickness)

gusset_body = Pos(bracket_thickness, bracket_thickness, bracket_thickness) * g.part
solid_body = solid_body + gusset_body

for i in range(3):
    x = hole_offset_from_corner + i * hole_spacing
    y = bracket_thickness / 2
    solid_body = solid_body - Pos(x, y, bracket_thickness - hole_cbore_depth/2) * Cylinder(hole_cbore_diameter/2, hole_cbore_depth)
    solid_body = solid_body - Pos(x, y, bracket_thickness/2) * Cylinder(hole_clearance/2, bracket_thickness)

for i in range(2):
    x = bracket_thickness / 2
    y = hole_offset_from_corner + i * hole_spacing
    solid_body = solid_body - Pos(x, y, bracket_thickness/2) * Cylinder(hole_clearance/2, bracket_thickness)

solid_body = fillet(solid_body.edges().filter_by(Axis.Z), fillet_radius)

part = solid_body
part.name = "L_Bracket"
export_step(part, "output.step")