from build123d import *

block_length = 80.0
block_width = 50.0
block_height = 60.0
wall_thickness = 5.0
central_hole_radius = 8.0
counterbore_radius = 12.0
counterbore_depth = 12.0
top_fillet_radius = 3.0
bottom_chamfer = 2.0
mount_hole_radius = 2.5
mount_hole_spacing = 30.0
rib_thickness = 5.0
rib_height = 20.0
rib_spacing = 30.0

solid = Box(block_length, block_width, block_height)

solid = solid - Pos(0, 0, block_height/2 - counterbore_depth/2) * Cylinder(counterbore_radius, counterbore_depth)
solid = solid - Pos(0, 0, 0) * Cylinder(central_hole_radius, block_height)

for x in [-mount_hole_spacing/2, mount_hole_spacing/2]:
    solid = solid - Pos(x, 0, block_height/2) * Rot(90, 0, 0) * Cylinder(mount_hole_radius, block_width)

for x in [-rib_spacing/2, rib_spacing/2]:
    solid = solid + Pos(x, 0, block_height/2 - rib_thickness/2) * Box(rib_thickness, rib_height, rib_thickness)

top_edges = solid.edges().filter_by(Axis.Z).sort_by(Axis.Z)[-2:]
solid = fillet(top_edges, top_fillet_radius)

bottom_face = solid.faces().sort_by(Axis.Z)[0]
solid = chamfer(bottom_face.edges(), bottom_chamfer)

part = solid
part.name = "block_with_holes_ribs_and_edges"
export_step(part, "output.step")