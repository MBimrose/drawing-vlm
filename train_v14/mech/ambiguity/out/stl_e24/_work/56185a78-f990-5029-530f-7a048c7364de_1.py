from build123d import *
import math

inner_diameter = 20.0
wall_thickness = 8.0
outer_diameter = inner_diameter + 2 * wall_thickness
collar_length = 30.0
set_screw_diameter = 4.0
set_screw_depth = wall_thickness + 2.0
set_screw_count = 3
set_screw_angle_offset = 0.0
relief_slot_width = 6.0
relief_slot_depth = 4.0
relief_slot_length = collar_length * 0.6
chamfer_size = 0.5
inner_radius = inner_diameter / 2.0
outer_radius = outer_diameter / 2.0

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            l1 = Line((inner_radius, 0), (outer_radius, 0))
            l2 = Line(l1@1, (outer_radius, collar_length))
            l3 = Line(l2@1, (inner_radius, collar_length))
            l4 = Line(l3@1, (inner_radius, 0))
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part

for i in range(set_screw_count):
    angle = math.radians(set_screw_angle_offset + i * 360.0 / set_screw_count)
    px = (inner_radius + wall_thickness / 2.0) * math.cos(angle)
    py = (inner_radius + wall_thickness / 2.0) * math.sin(angle)
    solid_body = solid_body - Pos(px, py, collar_length - set_screw_depth / 2) * Cylinder(set_screw_diameter / 2.0, set_screw_depth)

solid_body = solid_body - Pos(outer_radius - relief_slot_depth / 2.0, 0, collar_length / 2.0) * Box(relief_slot_depth, relief_slot_width, relief_slot_length)

solid_body = solid_body - Pos(outer_radius - relief_slot_depth / 2.0, 0, collar_length / 2.0) * Cylinder(relief_slot_width / 4.0, relief_slot_length)

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = chamfer(top_face.edges(), chamfer_size)

part = solid_body
part.name = "collar_with_set_screws"
export_step(part, "output.step")