from build123d import *

block_length = 80.0
block_width = 50.0
block_height = 30.0
boss_diameter = 20.0
boss_height = 20.0
fillet_radius = 4.0
chamfer_size = 2.0
mount_hole_dia = 6.0
mount_hole_spacing_x = 30.0
mount_hole_spacing_y = 30.0
pocket_length = 40.0
pocket_width = 25.0
pocket_depth = 15.0
pocket_fillet = 3.0
pocket_circle_dia = 12.0

solid_body = Box(block_length, block_width, block_height)
solid_body = solid_body + Cylinder(boss_diameter/2, boss_height)

solid_body = fillet(solid_body.edges().filter_by(Axis.Z), fillet_radius)

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = chamfer(top_face.edges(), chamfer_size)

for x, y in [(-mount_hole_spacing_x/2, -mount_hole_spacing_y/2),
             (mount_hole_spacing_x/2, -mount_hole_spacing_y/2),
             (-mount_hole_spacing_x/2, mount_hole_spacing_y/2),
             (mount_hole_spacing_x/2, mount_hole_spacing_y/2)]:
    solid_body = solid_body - Pos(x, y, 0) * Cylinder(mount_hole_dia/2, block_height + boss_height + 10)

with BuildPart() as pocket_bp:
    with BuildSketch() as ps:
        RectangleRounded(pocket_length, pocket_width, pocket_fillet)
        Circle(pocket_circle_dia/2, mode=Mode.SUBTRACT)
    extrude(amount=pocket_depth)
pocket_solid = pocket_bp.part

solid_body = solid_body - Pos(0, 0, block_height - pocket_depth) * pocket_solid

part = solid_body
part.name = "block_with_boss_and_pocket"
export_step(part, "output.step")