from build123d import *
import math

outer_diameter = 80.0
inner_diameter = 30.0
height = 40.0
groove_width = 5.0
groove_depth = 3.0
groove_position = 15.0
fillet_radius = 2.0
chamfer_distance = 1.0
mount_hole_diameter = 5.0
mount_hole_count = 3
mount_hole_radius = 35.0
rib_thickness = 3.0
rib_height = 20.0
rib_count = 3

outer_radius = outer_diameter / 2.0
inner_radius = inner_diameter / 2.0
groove_radius = inner_radius + groove_width

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            l1 = Line((outer_radius, 0), (outer_radius, height))
            l2 = Line(l1@1, (inner_radius, height))
            l3 = Line(l2@1, (inner_radius, groove_position + groove_depth))
            l4 = Line(l3@1, (groove_radius, groove_position + groove_depth))
            l5 = Line(l4@1, (groove_radius, groove_position))
            l6 = Line(l5@1, (inner_radius, groove_position))
            l7 = Line(l6@1, (inner_radius, 0))
            l8 = Line(l7@1, (outer_radius, 0))
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = fillet(top_face.edges(), fillet_radius)

solid_body = chamfer(solid_body.edges(), chamfer_distance)

for i in range(mount_hole_count):
    angle = math.radians(i * 360.0 / mount_hole_count)
    px = mount_hole_radius * math.cos(angle)
    py = mount_hole_radius * math.sin(angle)
    solid_body = solid_body - Pos(px, py, height/2) * Cylinder(mount_hole_diameter/2, height)

for i in range(rib_count):
    angle = i * 360.0 / rib_count
    rib = Rot(0, 0, angle) * Pos(outer_radius - rib_thickness/2, 0, height/2) * Box(rib_thickness, rib_thickness, rib_height)
    solid_body = solid_body + rib

part = solid_body
part.name = "revolved_ring_with_groove"
export_step(part, "output.step")