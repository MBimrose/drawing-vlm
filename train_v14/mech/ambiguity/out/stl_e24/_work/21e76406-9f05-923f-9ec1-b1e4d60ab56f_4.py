from build123d import *

vertical_leg_length = 70.0
horizontal_leg_length = 80.0
leg_thickness = 6.0
bracket_thickness = 6.0
gusset_height = 40.0
gusset_width = 12.0
gusset_thickness = 4.0
fillet_radius = 2.0
hole_diameter = 5.0
cbore_diameter = 7.5
cbore_depth = 2.0
hole_spacing = 20.0
hole_offset_from_corner = 15.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0,0), (horizontal_leg_length, 0), (horizontal_leg_length, leg_thickness),
                     (leg_thickness, leg_thickness), (leg_thickness, vertical_leg_length),
                     (0, vertical_leg_length), close=True)
        make_face()
    extrude(amount=bracket_thickness)

solid_body = p.part
solid_body = fillet(solid_body.edges().filter_by(Axis.Z), fillet_radius)

with BuildPart() as gp:
    with BuildSketch(Plane.YZ.offset(leg_thickness)) as gsk:
        with BuildLine() as gbl:
            Polyline((leg_thickness/2, 0), (leg_thickness/2 + gusset_width, 0),
                     (leg_thickness/2, gusset_height), close=True)
        make_face()
    extrude(amount=gusset_thickness)

solid_body = solid_body + gp.part

shaft_r = hole_diameter / 2
cbore_r = cbore_diameter / 2
top_z = bracket_thickness

solid_body = solid_body - Pos(leg_thickness/2, vertical_leg_length/2, top_z - cbore_depth/2) * Cylinder(cbore_r, cbore_depth)
solid_body = solid_body - Pos(leg_thickness/2, vertical_leg_length/2, top_z - 10) * Cylinder(shaft_r, 20)

for i in range(3):
    x = hole_offset_from_corner + i * hole_spacing
    solid_body = solid_body - Pos(x, leg_thickness/2, top_z - cbore_depth/2) * Cylinder(cbore_r, cbore_depth)
    solid_body = solid_body - Pos(x, leg_thickness/2, top_z - 10) * Cylinder(shaft_r, 20)

part = solid_body
part.name = "L_Bracket"
export_step(part, "output.step")