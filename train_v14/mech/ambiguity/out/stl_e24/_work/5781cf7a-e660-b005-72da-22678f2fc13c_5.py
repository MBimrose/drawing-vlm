from build123d import *

block_length = 80.0
block_width = 50.0
block_height = 30.0
wall_thickness = 2.0
dovetail_depth = 15.0
dovetail_top_width = 30.0
dovetail_bottom_width = 40.0
fillet_radius = 1.0
mount_hole_diameter = 4.0
mount_hole_offset = 10.0
rib_width = 5.0
rib_depth = 4.0
rib_height = 2.0
rib_spacing = 15.0

solid_body = Box(block_length, block_width, block_height)
top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[top_face])
solid_body = fillet(solid_body.edges().filter_by(Axis.Z), fillet_radius)

with BuildPart() as dovetail_bp:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            Polyline((-dovetail_top_width/2, 0), (dovetail_top_width/2, 0),
                     (dovetail_bottom_width/2, -dovetail_depth),
                     (-dovetail_bottom_width/2, -dovetail_depth), close=True)
        make_face()
    extrude(amount=block_width)
dovetail_solid = Pos(0, -block_width/2, 0) * dovetail_bp.part
solid_body = solid_body - dovetail_solid

hole_positions = [
    (-block_length/2 + mount_hole_offset, -block_width/2 + mount_hole_offset),
    (block_length/2 - mount_hole_offset, -block_width/2 + mount_hole_offset),
    (-block_length/2 + mount_hole_offset, block_width/2 - mount_hole_offset),
    (block_length/2 - mount_hole_offset, block_width/2 - mount_hole_offset),
]
for x, y in hole_positions:
    solid_body = solid_body - Pos(x, y, block_height/2) * Cylinder(mount_hole_diameter/2, block_height)

num_ribs = int((block_length - 2 * wall_thickness) // rib_spacing)
for i in range(num_ribs):
    x_pos = -block_length/2 + wall_thickness + rib_spacing/2 + i * rib_spacing
    rib = Pos(x_pos, 0, block_height/2 + rib_height/2) * Box(rib_width, rib_depth, rib_height)
    solid_body = solid_body + rib

part = solid_body
part.name = "dovetail_block_with_ribs"
export_step(part, "output.step")