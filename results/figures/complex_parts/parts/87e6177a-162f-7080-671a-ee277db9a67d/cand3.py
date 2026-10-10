from build123d import *
import math

outer_diameter = 80.0
wall_thickness = 5.0
height = 60.0
recess_diameter = 30.0
recess_depth = 10.0
mount_hole_diameter = 5.0
mount_hole_count = 4
mount_hole_radius = 30.0
slot_width = 4.0
slot_height = 12.0
slot_count = 6
chamfer_size = 1.0

outer_radius = outer_diameter / 2.0
inner_radius = outer_radius - wall_thickness

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            l1 = Line((outer_radius, 0), (outer_radius, height))
            l2 = Line(l1@1, (inner_radius, height))
            l3 = Line(l2@1, (inner_radius, 0))
            l4 = Line(l3@1, (outer_radius, 0))
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = chamfer(top_face.edges(), chamfer_size)

solid_body = solid_body - Pos(0, 0, height - recess_depth/2) * Cylinder(recess_diameter/2, recess_depth)

for i in range(mount_hole_count):
    angle = math.radians(i * 360.0 / mount_hole_count)
    px = mount_hole_radius * math.cos(angle)
    py = mount_hole_radius * math.sin(angle)
    solid_body = solid_body - Pos(px, py, height/2) * Cylinder(mount_hole_diameter/2, height)

for i in range(slot_count):
    angle = math.radians(i * 360.0 / slot_count)
    px = (outer_radius - wall_thickness/2) * math.cos(angle)
    py = (outer_radius - wall_thickness/2) * math.sin(angle)
    solid_body = solid_body - Pos(px, py, height/2) * Box(slot_width, wall_thickness, slot_height)

part = solid_body
part.name = "hollow_cylinder_with_features"
export_step(part, "output.step")