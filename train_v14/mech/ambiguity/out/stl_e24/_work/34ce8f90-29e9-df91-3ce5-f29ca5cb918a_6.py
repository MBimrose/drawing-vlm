from build123d import *

plate_length = 80.0
plate_width = 60.0
plate_thickness = 6.0
rib_length = 40.0
rib_width = 20.0
rib_height = 4.0
fillet_radius = 1.2
chamfer_distance = 0.8
hole_diameter = 4.0
hole_spacing_x = 30.0
hole_spacing_y = 20.0

with BuildPart() as p:
    with BuildSketch() as s:
        Rectangle(plate_length, plate_width)
    extrude(amount=plate_thickness)
    with BuildSketch(Plane.XY.offset(plate_thickness)) as s2:
        Rectangle(rib_length, rib_width)
    extrude(amount=rib_height)

solid = p.part
solid = chamfer(solid.edges().filter_by(Axis.Z), chamfer_distance)
top_face = solid.faces().sort_by(Axis.Z)[-1]
solid = fillet(top_face.edges(), fillet_radius)

hole_positions = [
    (-hole_spacing_x, -hole_spacing_y/2),
    (0, -hole_spacing_y/2),
    (hole_spacing_x, -hole_spacing_y/2),
    (-hole_spacing_x/2, hole_spacing_y/2),
    (hole_spacing_x/2, hole_spacing_y/2),
    (0, hole_spacing_y/2)
]

for x, y in hole_positions:
    solid = solid - Pos(x, y, 0) * Cylinder(hole_diameter/2, plate_thickness + rib_height + 10)

part = solid
part.name = "plate_with_rib_and_holes"
export_step(part, "output.step")