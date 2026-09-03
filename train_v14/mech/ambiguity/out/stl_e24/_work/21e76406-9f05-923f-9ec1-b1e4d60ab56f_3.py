from build123d import *

leg_vertical = 70.0
leg_horizontal = 80.0
thickness = 6.0
rib_height = 40.0
rib_thickness = 4.0
fillet_radius = 2.0
hole_diameter = 5.0
cbore_diameter = 7.5
cbore_depth = 2.0
hole_spacing = 25.0
hole_offset = 15.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0, 0), (0, leg_vertical), (thickness, leg_vertical),
                     (thickness, thickness), (leg_horizontal, thickness),
                     (leg_horizontal, 0), close=True)
        make_face()
    extrude(amount=thickness)

solid_body = p.part
solid_body = fillet(solid_body.edges().filter_by(Axis.Z), fillet_radius)

with BuildPart() as rib_p:
    with BuildSketch(Plane.YZ.offset(thickness)) as rib_sk:
        with BuildLine() as rib_bl:
            Polyline((thickness, 0), (thickness, rib_height), (thickness + rib_thickness, 0), close=True)
        make_face()
    extrude(amount=thickness)

solid_body = solid_body + rib_p.part

vertical_hole_y = leg_vertical - hole_offset
solid_body = solid_body - Pos(thickness/2, vertical_hole_y, thickness/2) * Cylinder(hole_diameter/2, thickness * 4)

for i in range(3):
    x = hole_offset + i * hole_spacing
    y = thickness / 2
    solid_body = solid_body - Pos(x, y, thickness/2) * Cylinder(hole_diameter/2, thickness * 4)
    solid_body = solid_body - Pos(x, y, thickness - cbore_depth/2) * Cylinder(cbore_diameter/2, cbore_depth)

part = solid_body
part.name = "L_Bracket"
export_step(part, "output.step")