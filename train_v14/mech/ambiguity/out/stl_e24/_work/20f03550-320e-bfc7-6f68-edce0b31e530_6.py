from build123d import *

leg_length = 70.0
leg_height = 50.0
thickness = 8.0
width = 12.0
fillet_radius = 2.0
hole_diameter = 5.0
hole_spacing = 20.0
hole_offset = 15.0
notch_width = 6.0
notch_depth = 4.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0, 0), (leg_length, 0), (leg_length, thickness),
                     (thickness, thickness), (thickness, leg_height + thickness),
                     (0, leg_height + thickness), close=True)
        make_face()
    extrude(amount=width)

solid_body = p.part
solid_body = fillet(solid_body.edges().filter_by(Axis.Z), fillet_radius)

notch = Pos(thickness/2, leg_height + thickness - notch_depth/2, width - notch_depth/2) * Box(notch_width, notch_depth, notch_depth)
solid_body = solid_body - notch

for i in range(3):
    x = hole_offset + i * hole_spacing
    y = thickness / 2
    hole = Pos(x, y, width/2) * Cylinder(hole_diameter/2, width)
    solid_body = solid_body - hole

part = solid_body
part.name = "L_Bracket"
export_step(part, "output.step")