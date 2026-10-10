from build123d import *

outer_diameter = 80.0
inner_diameter = 30.0
length = 100.0
rib_height = 5.0
rib_width = 20.0
rib_position = 40.0
counterbore_diameter = 60.0
counterbore_depth = 15.0
chamfer_size = 2.0
slot_width = 10.0
slot_depth = 5.0
slot_length = 60.0

outer_radius = outer_diameter / 2.0
inner_radius = inner_diameter / 2.0
rib_outer_radius = outer_radius + rib_height

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            Polyline((inner_radius, 0), (outer_radius, 0), (outer_radius, rib_position),
                     (rib_outer_radius, rib_position), (rib_outer_radius, rib_position + rib_width),
                     (outer_radius, rib_position + rib_width), (outer_radius, length),
                     (inner_radius, length), close=True)
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part
solid_body = solid_body - Pos(0, 0, length/2) * Cylinder(inner_radius, length)
solid_body = solid_body - Pos(0, 0, length - counterbore_depth/2) * Cylinder(counterbore_diameter/2, counterbore_depth)
solid_body = solid_body - Pos(outer_radius - slot_depth/2, length/2, 0) * Box(slot_depth, slot_length, slot_width)
solid_body = chamfer(solid_body.edges(), chamfer_size)

part = solid_body
part.name = "ribbed_cylinder_with_slot"
export_step(part, "output.step")