from build123d import *
import math

outer_radius = 45.0
inner_radius = 12.0
plate_thickness = 3.0
rim_width = 5.0
rim_height = 2.0
chamfer_size = 1.0
mount_hole_diameter = 6.0
mount_hole_offset = 20.0
vent_hole_diameter = 4.0
vent_hole_count = 12
vent_hole_radius = outer_radius - rim_width - 5.0

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            l1 = Line((inner_radius, 0), (inner_radius, plate_thickness))
            l2 = Line(l1@1, (outer_radius - rim_width, plate_thickness))
            l3 = Line(l2@1, (outer_radius, plate_thickness - rim_height))
            l4 = Line(l3@1, (outer_radius, 0))
            l5 = Line(l4@1, (inner_radius, 0))
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
top_edges = top_face.edges()
solid_body = chamfer(top_edges, chamfer_size)

for x, y in [(mount_hole_offset, 0), (-mount_hole_offset, 0), (0, mount_hole_offset), (0, -mount_hole_offset)]:
    solid_body = solid_body - Pos(x, y, 0) * Cylinder(mount_hole_diameter/2, plate_thickness * 2)

for i in range(vent_hole_count):
    angle = math.radians(i * 360.0 / vent_hole_count)
    px = vent_hole_radius * math.cos(angle)
    py = vent_hole_radius * math.sin(angle)
    solid_body = solid_body - Pos(px, py, 0) * Cylinder(vent_hole_diameter/2, plate_thickness * 2)

part = solid_body
part.name = "revolved_plate_with_holes"
export_step(part, "output.step")