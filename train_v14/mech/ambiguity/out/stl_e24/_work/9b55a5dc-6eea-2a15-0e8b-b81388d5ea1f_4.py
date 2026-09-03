from build123d import *

plate_length = 80.0
plate_width = 60.0
plate_thickness = 12.0
pocket_radius = 15.0
pocket_depth = 6.0
fillet_radius = 3.0
chamfer_size = 0.8
mount_hole_diameter = 4.0
mount_hole_offset = 15.0
rib_width = 10.0
rib_height = 4.0
rib_thickness = 2.0
cbore_radius = 2.0
cbore_outer_radius = 3.0
cbore_depth = 4.0

with BuildPart() as p:
    with BuildSketch() as s:
        Rectangle(plate_length, plate_width)
    extrude(amount=plate_thickness)

solid_body = p.part

rib = Pos(0, 0, plate_thickness - rib_thickness/2) * Box(rib_width, rib_height, rib_thickness)
solid_body = solid_body + rib

pocket = Pos(0, 0, plate_thickness - pocket_depth/2) * Cylinder(pocket_radius, pocket_depth)
solid_body = solid_body - pocket

hole_positions = [
    (-plate_length/2 + mount_hole_offset, -plate_width/2 + mount_hole_offset),
    ( plate_length/2 - mount_hole_offset, -plate_width/2 + mount_hole_offset),
    (-plate_length/2 + mount_hole_offset,  plate_width/2 - mount_hole_offset),
    ( plate_length/2 - mount_hole_offset,  plate_width/2 - mount_hole_offset),
]
for x, y in hole_positions:
    solid_body = solid_body - Pos(x, y, plate_thickness/2) * Cylinder(cbore_radius, plate_thickness)
    solid_body = solid_body - Pos(x, y, plate_thickness - cbore_depth/2) * Cylinder(cbore_outer_radius, cbore_depth)

vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = fillet(vertical_edges, fillet_radius)

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
top_edges = top_face.edges()
solid_body = chamfer(top_edges, chamfer_size)

part = solid_body
part.name = "plate_with_pocket_and_ribs"
export_step(part, "output.step")