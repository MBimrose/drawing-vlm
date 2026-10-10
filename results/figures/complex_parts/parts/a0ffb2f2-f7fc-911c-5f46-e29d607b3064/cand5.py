from build123d import *

shaft_length = 60.0
shaft_radius = 5.0
shoulder_length = 10.0
shoulder_radius = 15.0
tip_length = 5.0
tip_radius = 4.0
counterbore_diameter = 6.0
counterbore_depth = 8.0
shaft_hole_diameter = 3.0
chamfer_size = 0.5

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            Polyline((0, 0), (shaft_radius, 0), (shaft_radius, shaft_length - shoulder_length),
                     (shoulder_radius, shaft_length - shoulder_length), (shoulder_radius, shaft_length),
                     (tip_radius, shaft_length), (tip_radius, shaft_length + tip_length),
                     (0, shaft_length + tip_length), close=True)
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part
solid_body = solid_body - Pos(0, 0, shaft_length + tip_length - counterbore_depth/2) * Cylinder(counterbore_diameter/2, counterbore_depth)
solid_body = solid_body - Pos(0, 0, (shaft_length + tip_length)/2) * Cylinder(shaft_hole_diameter/2, shaft_length + tip_length + 20)
solid_body = chamfer(solid_body.edges(), chamfer_size)

part = solid_body
part.name = "revolved_shaft_with_holes"
export_step(part, "output.step")