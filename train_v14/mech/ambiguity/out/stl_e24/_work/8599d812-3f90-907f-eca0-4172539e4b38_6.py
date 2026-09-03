from build123d import *

plate_width = 80.0
plate_depth = 60.0
plate_thickness = 4.0
boss_width = 30.0
boss_depth = 20.0
boss_height = 2.0
pocket_width = 30.0
pocket_depth = 20.0
pocket_depth_cut = 2.0
hole_diameter = 3.0
hole_offset = 5.0
chamfer_size = 0.5
fillet_radius = 0.8

with BuildPart() as p:
    with BuildSketch() as s:
        Rectangle(plate_width, plate_depth)
    extrude(amount=plate_thickness)

solid_body = p.part
solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_size)
solid_body = fillet(solid_body.edges().filter_by(Axis.Z), fillet_radius)

boss = Pos(0, 0, plate_thickness + boss_height/2) * Box(boss_width, boss_depth, boss_height)
solid_body = solid_body + boss

pocket = Pos(0, 0, plate_thickness - pocket_depth_cut/2) * Box(pocket_width, pocket_depth, pocket_depth_cut)
solid_body = solid_body - pocket

hole_positions = [
    (-plate_width/2 + hole_offset, -plate_depth/2 + hole_offset),
    ( plate_width/2 - hole_offset, -plate_depth/2 + hole_offset),
    (-plate_width/2 + hole_offset,  plate_depth/2 - hole_offset),
    ( plate_width/2 - hole_offset,  plate_depth/2 - hole_offset)
]
for x, y in hole_positions:
    hole = Pos(x, y, plate_thickness/2) * Cylinder(hole_diameter/2, plate_thickness + 1)
    solid_body = solid_body - hole

part = solid_body
part.name = "plate_with_boss_pocket_holes"
export_step(part, "output.step")