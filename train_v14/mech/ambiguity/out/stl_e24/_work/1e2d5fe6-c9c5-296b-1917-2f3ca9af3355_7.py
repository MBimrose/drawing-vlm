from build123d import *
import math

outer_radius = 45.0
plate_thickness = 3.0
chamfer_distance = 2.0
central_hole_radius = 12.0
central_hole_depth = 2.0
peripheral_hole_radius = 2.0
peripheral_hole_count = 12
peripheral_hole_radius_offset = 5.0
mount_hole_radius = 3.0
mount_hole_distance = 20.0
mount_hole_count = 4
rib_width = 6.0
rib_height = 2.0
rib_offset = 10.0

with BuildPart() as p:
    with BuildSketch() as s:
        Circle(outer_radius)
    extrude(amount=plate_thickness)

solid_body = p.part

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
top_edges = top_face.edges()
solid_body = chamfer(top_edges, chamfer_distance)

solid_body = solid_body - Pos(0, 0, plate_thickness - central_hole_depth/2) * Cylinder(central_hole_radius, central_hole_depth)

for i in range(peripheral_hole_count):
    angle = math.radians(i * 360.0 / peripheral_hole_count)
    px = (outer_radius - peripheral_hole_radius_offset) * math.cos(angle)
    py = (outer_radius - peripheral_hole_radius_offset) * math.sin(angle)
    solid_body = solid_body - Pos(px, py, plate_thickness/2) * Cylinder(peripheral_hole_radius, plate_thickness)

for i in range(mount_hole_count):
    angle = math.radians(i * 360.0 / mount_hole_count)
    px = mount_hole_distance * math.cos(angle)
    py = mount_hole_distance * math.sin(angle)
    solid_body = solid_body - Pos(px, py, plate_thickness/2) * Cylinder(mount_hole_radius, plate_thickness)

rib = Pos(rib_offset, 0, plate_thickness/2) * Box(rib_width, rib_height, plate_thickness)
rib_mirror = mirror(rib, about=Plane.YZ)
solid_body = solid_body + rib + rib_mirror

part = solid_body
part.name = "plate_with_holes_and_ribs"
export_step(part, "output.step")