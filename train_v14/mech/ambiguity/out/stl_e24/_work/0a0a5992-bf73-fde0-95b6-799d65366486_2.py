from build123d import *

outer_diameter = 80.0
wall_thickness = 4.0
height = 70.0
base_thickness = 10.0
base_width = 40.0
base_length = 40.0
vent_diameter = 12.0
vent_offset = 30.0
mount_hole_diameter = 5.0
mount_hole_offset = 10.0
chamfer_size = 1.0

outer_radius = outer_diameter / 2.0
inner_radius = outer_radius - wall_thickness

with BuildPart() as p:
    with BuildSketch() as s:
        Circle(outer_radius)
    extrude(amount=height)

solid_body = p.part
top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[top_face])

base = Pos(0, 0, -base_thickness) * Box(base_width, base_length, base_thickness)
solid_body = solid_body + base

vent = Pos(outer_radius - wall_thickness/2, 0, vent_offset) * Rot(0, 90, 0) * Cylinder(vent_diameter/2, wall_thickness*2)
solid_body = solid_body - vent

for x, y in [(mount_hole_offset, mount_hole_offset), (-mount_hole_offset, mount_hole_offset),
             (mount_hole_offset, -mount_hole_offset), (-mount_hole_offset, -mount_hole_offset)]:
    solid_body = solid_body - Pos(x, y, -base_thickness/2) * Cylinder(mount_hole_diameter/2, base_thickness + 2)

bottom_face = solid_body.faces().sort_by(Axis.Z)[0]
solid_body = chamfer(bottom_face.edges(), chamfer_size)

part = solid_body
part.name = "hollow_cylinder_with_base"
export_step(part, "output.step")