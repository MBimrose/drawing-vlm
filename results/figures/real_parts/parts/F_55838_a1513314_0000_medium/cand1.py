from build123d import *

head_across_flats = 30.0
head_thickness = 20.0
shank_diameter = 12.0
shank_length = 60.0
fillet_radius = 5.0

with BuildPart() as p:
    with BuildSketch(Plane.YZ) as s:
        RegularPolygon(head_across_flats, 6)
    extrude(amount=head_thickness)

head = p.part
shank = Pos(head_thickness + shank_length/2, 0, 0) * Rot(0, 90, 0) * Cylinder(shank_diameter, shank_length)
result = head + shank
result = fillet(result.edges().filter_by(Axis.X), fillet_radius)

part = result
part.name = "hex_head_shank"
export_step(part, "output.step")