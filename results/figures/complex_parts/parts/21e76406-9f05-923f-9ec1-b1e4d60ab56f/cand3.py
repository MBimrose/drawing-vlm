from build123d import *

leg_length_vertical = 70.0
leg_length_horizontal = 80.0
leg_thickness = 6.0
rib_height = 40.0
rib_depth = 12.0
rib_thickness = 3.0
hole_diameter = 5.0
cbore_diameter = 7.5
cbore_depth = 2.0
hole_spacing = 25.0
hole_offset_from_corner = 15.0
fillet_radius = 2.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0, 0), (0, leg_length_vertical), (leg_thickness, leg_length_vertical),
                     (leg_thickness, leg_thickness), (leg_length_horizontal, leg_thickness),
                     (leg_length_horizontal, 0), close=True)
        make_face()
    extrude(amount=leg_thickness)

solid_body = p.part

with BuildPart() as rib_p:
    with BuildSketch(Plane.YZ) as rib_sk:
        with BuildLine() as rib_bl:
            Polyline((leg_thickness, 0), (leg_thickness + rib_depth, 0), (leg_thickness, rib_height), close=True)
        make_face()
    extrude(amount=rib_thickness)

solid_body = solid_body + rib_p.part

for i in range(3):
    x = hole_offset_from_corner + i * hole_spacing
    y = leg_thickness / 2
    solid_body = solid_body - Pos(x, y, leg_thickness - cbore_depth/2) * Cylinder(cbore_diameter/2, cbore_depth)
    solid_body = solid_body - Pos(x, y, leg_thickness/2) * Cylinder(hole_diameter/2, leg_thickness + 10)

for i in range(2):
    x = leg_thickness / 2
    y = hole_offset_from_corner + i * hole_spacing
    solid_body = solid_body - Pos(x, y, leg_thickness - cbore_depth/2) * Cylinder(cbore_diameter/2, cbore_depth)
    solid_body = solid_body - Pos(x, y, leg_thickness/2) * Cylinder(hole_diameter/2, leg_thickness + 10)

solid_body = fillet(solid_body.edges().filter_by(Axis.Z), fillet_radius)

part = solid_body
part.name = "L_Bracket"
export_step(part, "output.step")