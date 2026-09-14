from build123d import *

plate_width = 80.0
plate_height = 80.0
plate_thickness = 10.0
corner_radius = 10.0
pocket_margin = 4.0
pocket_depth = 5.0
hole_diameter = 8.0
hole_clearance = 0.1
fillet_radius = 4.0
rib_width = 5.0
rib_height = 5.0
rib_count = 4
boss_radius = 6.0
boss_height = 7.0
boss_offset = 30.0

solid_body = Box(plate_width, plate_height, plate_thickness)
solid_body = fillet(solid_body.edges().filter_by(Axis.Z), corner_radius)
bottom_face = solid_body.faces().sort_by(Axis.Z)[0]
solid_body = fillet(bottom_face.edges(), fillet_radius)

pocket_radius = (plate_width / 2) - pocket_margin
pocket = Pos(0, 0, plate_thickness/2 - pocket_depth/2) * Cylinder(pocket_radius, pocket_depth)
solid_body = solid_body - pocket

hole_r = (hole_diameter + hole_clearance) / 2
hole = Cylinder(hole_r, plate_thickness + 1)
solid_body = solid_body - hole

rib_length = (plate_width / 2) - corner_radius - rib_width
for i in range(rib_count):
    angle = i * 360.0 / rib_count
    rib = Rot(0, 0, angle) * Pos(rib_length/2, 0, rib_height/2) * Box(rib_length, rib_width, rib_height)
    solid_body = solid_body + rib

for x, y in [(boss_offset, boss_offset), (-boss_offset, boss_offset)]:
    boss = Pos(x, y, plate_thickness/2 + boss_height/2) * Cylinder(boss_radius, boss_height)
    solid_body = solid_body + boss

part = solid_body
part.name = "plate_with_pocket_ribs_bosses"
export_step(part, "output.step")