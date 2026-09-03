from build123d import *

outer_diameter = 80.0
inner_diameter = 30.0
length = 100.0
rib_height = 5.0
rib_width = 20.0
rib_start = (length - rib_width) / 2.0
counterbore_diameter = 60.0
counterbore_depth = 10.0
chamfer_size = 2.0
mount_hole_diameter = 8.0
mount_hole_spacing = 30.0
pocket_width = 20.0
pocket_height = 15.0
pocket_depth = 12.0
pocket_offset = 25.0

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            Polyline((0, 0), (outer_diameter/2, 0), (outer_diameter/2, rib_start),
                     (outer_diameter/2 + rib_height, rib_start), (outer_diameter/2 + rib_height, rib_start + rib_width),
                     (outer_diameter/2, rib_start + rib_width), (outer_diameter/2, length),
                     (0, length), close=True)
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part
solid_body = solid_body - Pos(0, 0, length/2) * Cylinder(inner_diameter/2, length)
solid_body = solid_body - Pos(0, 0, length - counterbore_depth/2) * Cylinder(counterbore_diameter/2, counterbore_depth)
solid_body = chamfer(solid_body.edges(), chamfer_size)

for z_pos in [length/2 - mount_hole_spacing/2, length/2 + mount_hole_spacing/2]:
    solid_body = solid_body - Pos(outer_diameter/2, 0, z_pos) * Rot(0, 90, 0) * Cylinder(mount_hole_diameter/2, length)

solid_body = solid_body - Pos(outer_diameter/2 + pocket_depth/2, pocket_offset, length/2) * Box(pocket_depth, pocket_width, pocket_height)

part = solid_body
part.name = "ribbed_shaft_with_pocket"
export_step(part, "output.step")