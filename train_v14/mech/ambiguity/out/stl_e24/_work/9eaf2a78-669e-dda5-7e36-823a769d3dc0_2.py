from build123d import *

long_leg_length = 80.0
short_leg_length = 50.0
leg_width = 12.0
thickness = 8.0
fillet_radius = 1.0
hole_diameter = 6.0
hole_depth = 5.0
hole_spacing = 10.0
slot_width = 6.0
slot_length = 10.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0,0), (long_leg_length,0), (long_leg_length,leg_width),
                     (leg_width,leg_width), (leg_width,short_leg_length+leg_width),
                     (0,short_leg_length+leg_width), close=True)
        make_face()
    extrude(amount=thickness)

solid = p.part
solid = fillet(solid.edges().filter_by(Axis.Z), fillet_radius)

for y in [leg_width/2 - hole_spacing/2, leg_width/2 + hole_spacing/2]:
    solid = solid - Pos(long_leg_length - hole_depth/2, y, thickness/2) * Rot(0, 90, 0) * Cylinder(hole_diameter/2, hole_depth)

slot_y = short_leg_length + leg_width/2
solid = solid - Pos(leg_width/2, slot_y, thickness/2) * Box(slot_length, slot_width, thickness)

part = solid
part.name = "L_Bracket"
export_step(part, "output.step")