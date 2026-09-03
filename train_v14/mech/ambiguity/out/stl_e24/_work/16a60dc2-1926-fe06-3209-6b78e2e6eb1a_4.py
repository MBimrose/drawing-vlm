from build123d import *

outer_diameter = 60.0
outer_radius = outer_diameter / 2.0
base_thickness = 5.0
rib_height = 8.0
rib_width = 6.0
rib_thickness = 4.0
blind_hole_diameter = 12.0
blind_hole_depth = base_thickness + rib_height - 2.0
chamfer_size = 1.0
mount_hole_diameter = 4.0
mount_hole_offset = 20.0

with BuildPart() as p:
    with BuildSketch() as s:
        Circle(outer_radius)
    extrude(amount=base_thickness + rib_height)

solid_body = p.part

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = chamfer(top_face.edges(), chamfer_size)

bottom_face = solid_body.faces().sort_by(Axis.Z)[0]
solid_body = chamfer(bottom_face.edges(), chamfer_size)

rib = Pos(0, 0, base_thickness + rib_height / 2) * Box(rib_width, rib_thickness, rib_height)
solid_body = solid_body + rib

blind_hole = Pos(0, 0, base_thickness + rib_height - blind_hole_depth / 2) * Cylinder(blind_hole_diameter / 2, blind_hole_depth)
solid_body = solid_body - blind_hole

for x, y in [(mount_hole_offset, mount_hole_offset), (-mount_hole_offset, mount_hole_offset),
             (-mount_hole_offset, -mount_hole_offset), (mount_hole_offset, -mount_hole_offset)]:
    mount_hole = Pos(x, y, (base_thickness + rib_height) / 2) * Cylinder(mount_hole_diameter / 2, base_thickness + rib_height + 1)
    solid_body = solid_body - mount_hole

part = solid_body
part.name = "ribbed_disc_with_holes"
export_step(part, "output.step")