from build123d import *
import math

outer_radius = 45.0
inner_radius = 12.0
thickness = 3.0
chamfer_size = 1.0
vent_hole_diameter = 4.0
vent_hole_count = 12
vent_hole_radius = outer_radius - 5.0
mount_hole_diameter = 6.0
mount_hole_offset = 20.0
rib_width = 6.0
rib_height = 2.0
rib_count = 4

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            l1 = Line((inner_radius, 0), (outer_radius, 0))
            l2 = Line(l1@1, (outer_radius, thickness))
            l3 = Line(l2@1, (inner_radius, thickness))
            l4 = Line(l3@1, (inner_radius, 0))
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
top_edges = top_face.edges()
solid_body = chamfer(top_edges, chamfer_size)

for i in range(vent_hole_count):
    angle = math.radians(i * 360.0 / vent_hole_count)
    px = vent_hole_radius * math.cos(angle)
    py = vent_hole_radius * math.sin(angle)
    solid_body = solid_body - Pos(px, py, thickness/2) * Cylinder(vent_hole_diameter/2, thickness)

for x, y in [(mount_hole_offset, 0), (-mount_hole_offset, 0), (0, mount_hole_offset), (0, -mount_hole_offset)]:
    solid_body = solid_body - Pos(x, y, thickness/2) * Cylinder(mount_hole_diameter/2, thickness)

rib_angle_step = 360.0 / rib_count
for i in range(rib_count):
    angle = math.radians(i * rib_angle_step)
    px = (inner_radius + rib_width/2) * math.cos(angle)
    py = (inner_radius + rib_width/2) * math.sin(angle)
    rib = Pos(px, py, thickness/2) * Rot(0, 0, i * rib_angle_step) * Box(rib_width, rib_height, thickness)
    solid_body = solid_body + rib

part = solid_body
part.name = "washer_with_ribs"
export_step(part, "output.step")