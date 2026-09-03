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
mount_hole_offset = 20.0
pocket_radius = 8.0
pocket_depth = 1.5
rib_width = 6.0
rib_height = 2.0
rib_offset = outer_radius / 2.0

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            l1 = Line((inner_radius, 0), (outer_radius, 0))
            l2 = Line(l1@1, (outer_radius, plate_thickness))
            l3 = Line(l2@1, (inner_radius, plate_thickness))
            l4 = Line(l3@1, (inner_radius, 0))
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part
top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = chamfer(top_face.edges(), chamfer_distance)

for i in range(hole_count):
    a = math.radians(i * 360.0 / hole_count)
    solid_body = solid_body - Pos(hole_radius * math.cos(a), hole_radius * math.sin(a), plate_thickness/2) * Cylinder(hole_diameter/2, plate_thickness)

for x, y in [(mount_hole_offset, 0), (-mount_hole_offset, 0), (0, mount_hole_offset), (0, -mount_hole_offset)]:
    solid_body = solid_body - Pos(x, y, plate_thickness/2) * Cylinder(mount_hole_diameter/2, plate_thickness)

solid_body = solid_body - Pos(0, 0, plate_thickness - pocket_depth/2) * Cylinder(pocket_radius, pocket_depth)
solid_body = solid_body + Pos(rib_offset, 0, plate_thickness/2) * Box(rib_width, rib_height, plate_thickness)

part = solid_body
part.name = "washer_with_rib"
export_step(part, "output.step")