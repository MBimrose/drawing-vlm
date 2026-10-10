from build123d import *
import math

outer_diameter = 80.0
inner_diameter = 30.0
length = 100.0
rib_height = 5.0
rib_width = 20.0
rib_position = 40.0
counterbore_diameter = 60.0
counterbore_depth = 15.0
chamfer_size = 2.0
mount_hole_diameter = 6.0
mount_hole_radius = 45.0
mount_hole_count = 2

outer_radius = outer_diameter / 2.0
inner_radius = inner_diameter / 2.0
rib_outer_radius = outer_radius + rib_height

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            l1 = Line((inner_radius, 0), (outer_radius, 0))
            l2 = Line(l1@1, (outer_radius, rib_position))
            l3 = Line(l2@1, (rib_outer_radius, rib_position))
            l4 = Line(l3@1, (rib_outer_radius, rib_position + rib_width))
            l5 = Line(l4@1, (outer_radius, rib_position + rib_width))
            l6 = Line(l5@1, (outer_radius, length))
            l7 = Line(l6@1, (inner_radius, length))
            l8 = Line(l7@1, (inner_radius, 0))
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part
solid_body = chamfer(solid_body.edges(), chamfer_size)

solid_body = solid_body - Pos(0, 0, length - counterbore_depth/2) * Cylinder(counterbore_diameter/2, counterbore_depth)

for i in range(mount_hole_count):
    angle = math.radians(i * 360.0 / mount_hole_count)
    px = mount_hole_radius * math.cos(angle)
    py = mount_hole_radius * math.sin(angle)
    solid_body = solid_body - Pos(px, py, length/2) * Cylinder(mount_hole_diameter/2, length + 20)

part = solid_body
part.name = "revolved_ribbed_cylinder"
export_step(part, "output.step")