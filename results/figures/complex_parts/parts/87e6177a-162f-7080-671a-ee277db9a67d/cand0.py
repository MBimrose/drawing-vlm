from build123d import *
import math

outer_diameter = 80.0
wall_thickness = 5.0
height = 60.0
vent_width = 30.0
vent_height = 10.0
vent_offset_z = 20.0
mount_hole_diameter = 5.0
mount_hole_radius = 15.0
mount_hole_count = 4
chamfer_size = 1.0
rib_thickness = 2.0
rib_height = 10.0
rib_count = 6
rib_offset_z = 5.0

outer_radius = outer_diameter / 2.0
inner_radius = outer_radius - wall_thickness

with BuildPart() as p:
    with BuildSketch() as s:
        Circle(outer_radius)
    extrude(amount=height)

solid_body = p.part
top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[top_face])

vent_cut = Pos(outer_radius - wall_thickness/2, vent_offset_z, 0) * Box(wall_thickness + 0.2, vent_width, vent_height)
solid_body = solid_body - vent_cut

for i in range(mount_hole_count):
    angle = math.radians(i * 360.0 / mount_hole_count)
    px = mount_hole_radius * math.cos(angle)
    py = mount_hole_radius * math.sin(angle)
    hole = Pos(px, py, 0) * Cylinder(mount_hole_diameter/2, height + 2)
    solid_body = solid_body - hole

for i in range(rib_count):
    angle = math.radians(i * 360.0 / rib_count)
    px = (inner_radius - rib_thickness/2) * math.cos(angle)
    py = (inner_radius - rib_thickness/2) * math.sin(angle)
    rib = Pos(px, py, rib_offset_z) * Box(rib_thickness, rib_thickness, rib_height)
    solid_body = solid_body + rib

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
top_edges = top_face.edges()
solid_body = chamfer(top_edges, chamfer_size)

part = solid_body
part.name = "vented_cylinder_with_ribs"
export_step(part, "output.step")