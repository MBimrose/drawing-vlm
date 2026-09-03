from build123d import *
import math

outer_radius = 45.0
inner_radius = 12.0
plate_thickness = 3.0
chamfer_distance = 1.0
hole_diameter = 4.0
hole_count = 12
hole_radius = outer_radius - 5.0
mount_hole_diameter = 6.0
mount_hole_count = 4
mount_hole_radius = inner_radius + 8.0

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            Line((inner_radius, 0), (outer_radius, 0))
            Line((outer_radius, 0), (outer_radius, plate_thickness))
            Line((outer_radius, plate_thickness), (inner_radius, plate_thickness))
            Line((inner_radius, plate_thickness), (inner_radius, 0))
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part
top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = chamfer(top_face.edges(), chamfer_distance)

for i in range(hole_count):
    angle = math.radians(i * 360.0 / hole_count)
    px = hole_radius * math.cos(angle)
    py = hole_radius * math.sin(angle)
    solid_body = solid_body - Pos(px, py, plate_thickness/2) * Cylinder(hole_diameter/2, plate_thickness)

for i in range(mount_hole_count):
    angle = math.radians(i * 360.0 / mount_hole_count)
    px = mount_hole_radius * math.cos(angle)
    py = mount_hole_radius * math.sin(angle)
    solid_body = solid_body - Pos(px, py, plate_thickness/2) * Cylinder(mount_hole_diameter/2, plate_thickness)

part = solid_body
part.name = "washer_plate"
export_step(part, "output.step")