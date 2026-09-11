from build123d import *

plate_width = 80.0
plate_depth = 80.0
plate_thickness = 10.0
corner_fillet_radius = 10.0
edge_fillet_radius = 4.0
recess_radius = 36.0
recess_depth = 6.0
central_hole_diameter = 8.0
rib_width = 5.0
rib_height = 4.0
rib_count = 6
boss_radius = 8.0
boss_height = 7.0
boss_offset = 30.0
notch_width = 12.0
notch_depth = 6.0

solid_body = Box(plate_width, plate_depth, plate_thickness)
solid_body = fillet(solid_body.edges().filter_by(Axis.Z), corner_fillet_radius)
bottom_face = solid_body.faces().sort_by(Axis.Z)[0]
solid_body = fillet(bottom_face.edges(), edge_fillet_radius)

recess = Pos(0, 0, plate_thickness/2 - recess_depth/2) * Cylinder(recess_radius, recess_depth)
solid_body = solid_body - recess

hole = Cylinder(central_hole_diameter/2, plate_thickness + 2)
solid_body = solid_body - hole

rib_length = recess_radius - central_hole_diameter/2
rib = Pos(central_hole_diameter/2 + rib_length/2, 0, -plate_thickness/2 + rib_height/2) * Box(rib_width, rib_length, rib_height)
ribs = rib
for i in range(1, rib_count):
    angle = i * 360.0 / rib_count
    ribs = ribs + Rot(0, 0, angle) * rib
solid_body = solid_body + ribs

boss = Pos(boss_offset, boss_offset, plate_thickness/2 + boss_height/2) * Cylinder(boss_radius, boss_height)
bosses = boss
for x, y in [(-boss_offset, boss_offset), (-boss_offset, -boss_offset), (boss_offset, -boss_offset)]:
    bosses = bosses + Pos(x, y, plate_thickness/2 + boss_height/2) * Cylinder(boss_radius, boss_height)
solid_body = solid_body + bosses

notch = Pos(plate_width/2 - notch_width/2, plate_depth/2 - notch_depth/2, 0) * Box(notch_width, notch_depth, plate_thickness + 2)
notches = notch
for x, y in [(-plate_width/2 + notch_width/2, plate_depth/2 - notch_depth/2),
             (-plate_width/2 + notch_width/2, -plate_depth/2 + notch_depth/2),
             (plate_width/2 - notch_width/2, -plate_depth/2 + notch_depth/2)]:
    notches = notches + Pos(x, y, 0) * Box(notch_width, notch_depth, plate_thickness + 2)
solid_body = solid_body - notches

part = solid_body
part.name = "plate_with_recess_ribs_bosses"
export_step(part, "output.step")