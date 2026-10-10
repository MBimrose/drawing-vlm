from build123d import *

plate_length = 80.0
plate_width = 50.0
plate_thickness = 10.0
boss_diameter = 40.0
boss_height = 20.0
nozzle_height = 30.0
nozzle_tip_diameter = 10.0
chamfer_size = 1.0
mount_hole_diameter = 6.0
mount_hole_offset = 10.0

base = Pos(0, 0, plate_thickness/2) * Box(plate_length, plate_width, plate_thickness)
boss = Pos(0, 0, plate_thickness + boss_height/2) * Cylinder(boss_diameter/2, boss_height)
nozzle = Pos(0, 0, plate_thickness + boss_height + nozzle_height/2) * Cone(boss_diameter/2, nozzle_tip_diameter/2, nozzle_height)

solid_body = base + boss + nozzle

top_edges = solid_body.edges().sort_by(Axis.Z)[-1:]
solid_body = chamfer(top_edges, chamfer_size)

hole_positions = [
    (-plate_length/2 + mount_hole_offset, -plate_width/2 + mount_hole_offset),
    ( plate_length/2 - mount_hole_offset, -plate_width/2 + mount_hole_offset),
    (-plate_length/2 + mount_hole_offset,  plate_width/2 - mount_hole_offset),
    ( plate_length/2 - mount_hole_offset,  plate_width/2 - mount_hole_offset),
]

for x, y in hole_positions:
    solid_body = solid_body - Pos(x, y, 0) * Cylinder(mount_hole_diameter/2, 200)

part = solid_body
part.name = "plate_with_boss_nozzle"
export_step(part, "output.step")