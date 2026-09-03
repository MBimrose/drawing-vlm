from build123d import *

length = 80.0
width = 50.0
thickness = 12.0
notch_width = 20.0
notch_depth = 20.0
hole_diameter = 6.0
hole_spacing = 25.0
chamfer_distance = 5.0
rib_width = 6.0
rib_height = 10.0
rib_spacing = 15.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline(
                (-length/2, -width/2),
                (length/2, -width/2),
                (length/2, width/2 - notch_depth),
                (length/2 - notch_width, width/2),
                (-length/2, width/2),
                close=True
            )
        make_face()
    extrude(amount=thickness)

solid = p.part

for x, y in [(-hole_spacing, 0), (0, 0), (hole_spacing, 0)]:
    solid = solid - Pos(x, y, 0) * Cylinder(hole_diameter/2, thickness * 2)

solid = chamfer(solid.edges().filter_by(Axis.Z), chamfer_distance)

for x, y in [(-rib_spacing/2, 0), (rib_spacing/2, 0)]:
    solid = solid + Pos(x, y, -rib_height/2) * Box(rib_width, rib_height, rib_height)

part = solid
part.name = "notched_plate_with_ribs"
export_step(part, "output.step")