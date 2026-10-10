from build123d import *

outer_diameter = 80.0
inner_diameter = 30.0
length = 100.0
shoulder_diameter = 60.0
shoulder_length = 20.0
rib_height = 5.0
rib_width = 20.0
set_screw_diameter = 8.0
set_screw_offset = 30.0
chamfer_size = 2.0

outer_radius = outer_diameter / 2.0
inner_radius = inner_diameter / 2.0
shoulder_radius = shoulder_diameter / 2.0
rib_outer_radius = outer_radius + rib_height

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            Polyline((inner_radius, 0), (outer_radius, 0), (outer_radius, (length - rib_width) / 2),
                     (rib_outer_radius, (length - rib_width) / 2), (rib_outer_radius, (length + rib_width) / 2),
                     (outer_radius, (length + rib_width) / 2), (outer_radius, length - shoulder_length),
                     (shoulder_radius, length - shoulder_length), (shoulder_radius, length),
                     (inner_radius, length), close=True)
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part
solid_body = solid_body - Pos(0, 0, length / 2) * Cylinder(inner_radius, length)
solid_body = solid_body - Pos(0, 0, length - shoulder_length / 2) * Cylinder(shoulder_radius, shoulder_length)
solid_body = solid_body - Pos(set_screw_offset, outer_radius, length / 2) * Rot(90, 0, 0) * Cylinder(set_screw_diameter / 2, outer_radius * 2)
solid_body = chamfer(solid_body.edges(), chamfer_size)

part = solid_body
part.name = "stepped_shaft_with_rib"
export_step(part, "output.step")