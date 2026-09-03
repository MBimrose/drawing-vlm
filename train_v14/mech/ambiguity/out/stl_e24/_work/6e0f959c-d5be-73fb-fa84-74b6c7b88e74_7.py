from build123d import *

block_length = 80.0
block_width = 50.0
block_height = 15.0
wall_thickness = 3.0
pocket_length = 30.0
pocket_width = 25.0
pocket_depth = 8.0
fillet_radius = 2.0
chamfer_distance = 1.0
mount_hole_diameter = 2.5
mount_hole_offset = 12.0
rib_thickness = 2.0
rib_height = 5.0
counterbore_diameter = 6.0
counterbore_depth = 4.0

solid_body = Box(block_length, block_width, block_height)

pocket_cut = Pos(block_length/2 - pocket_depth/2, -block_length/2 + pocket_length/2, 0) * Box(pocket_depth, pocket_length, pocket_width)
solid_body = solid_body - pocket_cut

pocket_edges = solid_body.edges().filter_by(Axis.Z).sort_by(Axis.X)[:2]
solid_body = fillet(pocket_edges, fillet_radius)

chamfer_edges = solid_body.edges().filter_by(Axis.Z).sort_by(Axis.Y)[-2:]
solid_body = chamfer(chamfer_edges, chamfer_distance)

for x, y in [(mount_hole_offset, mount_hole_offset), (-mount_hole_offset, mount_hole_offset),
             (mount_hole_offset, -mount_hole_offset), (-mount_hole_offset, -mount_hole_offset)]:
    solid_body = solid_body - Pos(x, y, 0) * Cylinder(mount_hole_diameter/2, block_height + 1)

rib1 = Pos(0, block_width/2 - rib_thickness/2, 0) * Box(block_length, rib_thickness, rib_height)
rib2 = Pos(0, -block_width/2 + rib_thickness/2, 0) * Box(block_length, rib_thickness, rib_height)
solid_body = solid_body + rib1 + rib2

cbore_cut = Pos(block_length/2 - counterbore_depth/2, -block_width/2 + 10, 0) * Rot(0, 90, 0) * Cylinder(counterbore_diameter/2, counterbore_depth)
solid_body = solid_body - cbore_cut

part = solid_body
part.name = "block_with_pocket_ribs_and_holes"
export_step(part, "output.step")