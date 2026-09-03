from build123d import *

outer_diameter = 80.0
wall_thickness = 4.0
length = 70.0
vent_diameter = 12.0
vent_offset = 30.0
base_width = 40.0
base_length = 40.0
base_thickness = 14.0
mount_hole_diameter = 5.0
mount_hole_spacing = 20.0
chamfer_distance = 1.0

outer_radius = outer_diameter / 2.0
inner_radius = outer_radius - wall_thickness

with BuildPart() as p:
    with BuildSketch() as s:
        Circle(outer_radius)
    extrude(amount=length)

solid_body = p.part
top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[top_face])

vent_cyl = Pos(outer_radius, 0, vent_offset) * Rot(0, 90, 0) * Cylinder(vent_diameter / 2.0, outer_diameter * 2)
solid_body = solid_body - vent_cyl

base = Pos(0, 0, -base_thickness / 2) * Box(base_width, base_length, base_thickness)
solid_body = solid_body + base

for x, y in [(-mount_hole_spacing / 2, -mount_hole_spacing / 2),
             (mount_hole_spacing / 2, -mount_hole_spacing / 2),
             (-mount_hole_spacing / 2, mount_hole_spacing / 2),
             (mount_hole_spacing / 2, mount_hole_spacing / 2)]:
    hole = Pos(x, y, -base_thickness / 2) * Cylinder(mount_hole_diameter / 2, base_thickness + 10)
    solid_body = solid_body - hole

top_edges = solid_body.edges().sort_by(Axis.Z)[-1:]
solid_body = chamfer(top_edges, chamfer_distance)

bottom_edges = solid_body.edges().sort_by(Axis.Z)[:1]
solid_body = chamfer(bottom_edges, chamfer_distance)

part = solid_body
part.name = "vented_cylinder_with_base"
export_step(part, "output.step")