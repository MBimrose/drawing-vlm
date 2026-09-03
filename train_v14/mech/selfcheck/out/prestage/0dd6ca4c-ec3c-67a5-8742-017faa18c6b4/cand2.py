from build123d import *

total_length = 80.0
base_radius = 15.0
mid_radius = 25.0
tip_radius = 10.0
base_section_length = 15.0
mid_section_length = 30.0
tip_section_length = total_length - base_section_length - mid_section_length
hole_diameter = 10.0
countersink_diameter = 16.0
countersink_angle = 82.0
chamfer_size = 1.0

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            Polyline((0, 0), (base_radius, 0), (base_radius, base_section_length),
                     (mid_radius, base_section_length + mid_section_length),
                     (tip_radius, total_length), (0, total_length), close=True)
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part
solid_body = solid_body - CounterSinkHole(hole_diameter/2, countersink_diameter/2, total_length, countersink_angle)
solid_body = chamfer(solid_body.edges(), chamfer_size)

part = solid_body
part.name = "revolved_profile_with_countersink"
export_step(part, "output.step")