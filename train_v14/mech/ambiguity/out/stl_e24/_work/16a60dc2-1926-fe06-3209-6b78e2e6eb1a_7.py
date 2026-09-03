from build123d import *

outer_radius = 30
inner_radius = 12
height = 15
wall_thickness = 1
chamfer_distance = 1
central_hole_diameter = 12
mount_hole_diameter = 4
mount_hole_offset = 20

with BuildPart() as p:
    with BuildSketch() as s:
        Circle(outer_radius)
        Circle(inner_radius)
    extrude(amount=height)

solid_body = p.part
solid_body = offset(solid_body, amount=-wall_thickness)
solid_body = chamfer(solid_body.edges(), chamfer_distance)

solid_body = solid_body - Pos(0, 0, height/2) * Cylinder(central_hole_diameter/2, height + 1)

for x, y in [(mount_hole_offset, mount_hole_offset), (-mount_hole_offset, mount_hole_offset),
             (mount_hole_offset, -mount_hole_offset), (-mount_hole_offset, -mount_hole_offset)]:
    solid_body = solid_body - Pos(x, y, height/2) * Cylinder(mount_hole_diameter/2, height + 1)

part = solid_body
part.name = "hollow_cylinder_with_holes"
export_step(part, "output.step")