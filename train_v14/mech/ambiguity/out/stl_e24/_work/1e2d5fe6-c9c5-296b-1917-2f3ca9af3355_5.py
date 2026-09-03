from build123d import *
import math

outer_radius = 45.0
inner_radius = 12.0
plate_thickness = 3.0
chamfer_distance = 2.0
hole_diameter = 4.0
hole_count = 12
hole_radius = outer_radius - 5.0
mount_hole_diameter = 6.0
mount_hole_count = 4
mount_hole_radius = 20.0

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            l1 = Line((inner_radius, 0), (outer_radius, 0))
            l2 = Line(l1 @ 1, (outer_radius, plate_thickness))
            l3 = Line(l2 @ 1, (inner_radius, plate_thickness))
            l4 = Line(l3 @ 1, (inner_radius, 0))
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
top_edges = top_face.edges()
solid_body = chamfer(top_edges, chamfer_distance)

for i in range(hole_count):
    angle = math.radians(i * 360.0 / hole_count)
    px = hole_radius * math.cos(angle)
    py = hole_radius * math.sin(angle)
    solid_body = solid_body - Pos(px, py, 0) * Cylinder(hole_diameter / 2, plate_thickness * 2)

for i in range(mount_hole_count):
    angle = math.radians(i * 360.0 / mount_hole_count)
    px = mount_hole_radius * math.cos(angle)
    py = mount_hole_radius * math.sin(angle)
    solid_body = solid_body - Pos(px, py, 0) * Cylinder(mount_hole_diameter / 2, plate_thickness * 2)

part = solid_body
part.name = "washer_plate"
export_step(part, "output.step")