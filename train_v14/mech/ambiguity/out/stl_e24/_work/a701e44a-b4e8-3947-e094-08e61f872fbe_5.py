from build123d import *

leg_width = 20.0
vertical_leg_length = 50.0
horizontal_leg_length = 60.0
thickness = 8.0
fillet_radius = 4.0
mount_hole_diameter = 5.0
mount_hole_depth = 6.0
countersink_diameter = 9.0
countersink_angle = 82.0
rib_width = 6.0
rib_height = 12.0
rib_thickness = 2.0
rib_spacing = 8.0
rib_count = 3

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0,0), (0, vertical_leg_length), (leg_width, vertical_leg_length),
                     (leg_width, vertical_leg_length + leg_width),
                     (leg_width + horizontal_leg_length, vertical_leg_length + leg_width),
                     (leg_width + horizontal_leg_length, 0), close=True)
        make_face()
    extrude(amount=thickness)

solid = p.part
edges = solid.edges().filter_by(Axis.Z).sort_by(Axis.X)[-2:]
solid = fillet(edges, fillet_radius)

hole = CounterSinkHole(mount_hole_diameter/2, countersink_diameter/2, mount_hole_depth, countersink_angle)
solid = solid - Pos(leg_width/2, vertical_leg_length + leg_width/2, thickness) * hole

for i in range(rib_count):
    x = leg_width + rib_spacing/2 + i * (rib_width + rib_spacing)
    y = leg_width/2
    rib = Pos(x, y, rib_thickness/2) * Box(rib_width, rib_height, rib_thickness)
    solid = solid + rib

part = solid
part.name = "L_Bracket"
export_step(part, "output.step")