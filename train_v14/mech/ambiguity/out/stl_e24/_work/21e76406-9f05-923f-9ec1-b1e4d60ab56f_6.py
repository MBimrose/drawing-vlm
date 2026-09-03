from build123d import *

vertical_leg_length = 70.0
horizontal_leg_length = 80.0
leg_thickness = 6.0
leg_width = 6.0
gusset_height = 12.0
gusset_thickness = 4.0
fillet_radius = 2.0
hole_diameter = 5.0
cbore_diameter = 7.5
cbore_depth = 2.0
hole_offset = 15.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0, 0), (0, vertical_leg_length), (leg_thickness, vertical_leg_length),
                     (leg_thickness, leg_thickness), (horizontal_leg_length, leg_thickness),
                     (horizontal_leg_length, 0), close=True)
        make_face()
    extrude(amount=leg_width)

solid_body = p.part
solid_body = fillet(solid_body.edges().filter_by(Axis.Z), fillet_radius)

with BuildPart() as g:
    with BuildSketch(Plane.YZ) as gsk:
        with BuildLine() as gbl:
            Polyline((0, 0), (gusset_height, 0), (0, horizontal_leg_length), close=True)
        make_face()
    extrude(amount=gusset_thickness)

solid_body = solid_body + g.part

shaft_r = hole_diameter / 2
cbore_r = cbore_diameter / 2
top_z = horizontal_leg_length

for x, y in [(horizontal_leg_length/3, leg_thickness/2), (2*horizontal_leg_length/3, leg_thickness/2)]:
    solid_body = solid_body - Pos(x, y, top_z - cbore_depth/2) * Cylinder(cbore_r, cbore_depth)
    solid_body = solid_body - Pos(x, y, top_z/2) * Cylinder(shaft_r, top_z + 10)

for x, y in [(leg_thickness/2, vertical_leg_length/3), (leg_thickness/2, 2*vertical_leg_length/3)]:
    solid_body = solid_body - Pos(x, y, top_z - cbore_depth/2) * Cylinder(cbore_r, cbore_depth)
    solid_body = solid_body - Pos(x, y, top_z/2) * Cylinder(shaft_r, top_z + 10)

part = solid_body
part.name = "L_Bracket"
export_step(part, "output.step")