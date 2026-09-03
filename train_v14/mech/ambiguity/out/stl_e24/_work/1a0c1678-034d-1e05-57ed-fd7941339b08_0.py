from build123d import *

leg_long = 80.0
leg_short = 50.0
thickness = 8.0
depth = 8.0
fillet_radius = 2.0
hole_diameter = 5.0
hole_spacing = 12.0
hole_offset = 15.0
pocket_width = 30.0
pocket_height = 20.0
pocket_depth = 4.0
short_hole_diameter = 6.0
short_hole_spacing = 20.0
short_hole_offset = 15.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0, 0), (leg_long, 0), (leg_long, thickness), (thickness, thickness), (thickness, leg_short), (0, leg_short), close=True)
        make_face()
    extrude(amount=depth)

solid_body = p.part
solid_body = fillet(solid_body.edges().filter_by(Axis.Z), fillet_radius)

for i in range(4):
    x = hole_offset + i * hole_spacing
    y = thickness / 2
    solid_body = solid_body - Pos(x, y, 0) * Cylinder(hole_diameter / 2, depth * 2)

for i in range(2):
    y = short_hole_offset + i * short_hole_spacing
    z = depth / 2
    solid_body = solid_body - Pos(0, y, z) * Rot(0, 90, 0) * Cylinder(short_hole_diameter / 2, leg_long * 2)

pocket = Pos(leg_long - pocket_depth / 2, thickness / 2, depth / 2) * Box(pocket_depth, pocket_width, pocket_height)
solid_body = solid_body - pocket

part = solid_body
part.name = "L_Bracket"
export_step(part, "output.step")