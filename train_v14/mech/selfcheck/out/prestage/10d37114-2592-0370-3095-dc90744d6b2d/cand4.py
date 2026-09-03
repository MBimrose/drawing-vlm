from build123d import *

outer_radius = 30.0
inner_radius = 15.0
length = 60.0
shoulder_radius = 25.0
shoulder_length = 15.0
fillet_radius = 2.0
hole_diameter = 5.0
hole_spacing = 40.0

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            Polyline((outer_radius, 0), (outer_radius, length), (inner_radius, length),
                     (inner_radius, length - shoulder_length), (shoulder_radius, length - shoulder_length),
                     (shoulder_radius, 0), close=True)
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part
solid_body = fillet(solid_body.edges(), fillet_radius)

for x in [-hole_spacing/2, hole_spacing/2]:
    solid_body = solid_body - Pos(x, 0, length/2) * Cylinder(hole_diameter/2, length + 20)

part = solid_body
part.name = "revolved_part_with_holes"
export_step(part, "output.step")