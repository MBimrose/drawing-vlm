from build123d import *
import math

plate_width = 80.0
plate_depth = 80.0
plate_thickness = 8.0
pocket_width = 50.0
pocket_depth = 50.0
pocket_depth_cut = 6.0
slot_length = 30.0
slot_width = 6.0
slot_depth = 4.0
boss_size = 12.0
boss_height = 6.0
boss_hole_diameter = 3.0
boss_csk_diameter = 6.0
boss_csk_angle = 82.0
chamfer_size = 2.0

result = Box(plate_width, plate_depth, plate_thickness)

pocket = Pos(0, 0, plate_thickness - pocket_depth_cut/2) * Box(pocket_width, pocket_depth, pocket_depth_cut)
result = result - pocket

slot1 = Pos(-plate_width/2 + slot_length/2, 0, plate_thickness - slot_depth/2) * Box(slot_length, slot_width, slot_depth)
result = result - slot1

slot2 = Pos(0, -plate_depth/2 + slot_length/2, plate_thickness - slot_depth/2) * Box(slot_length, slot_width, slot_depth)
result = result - slot2

csk_radius = boss_csk_diameter / 2
csk_height = csk_radius / math.tan(math.radians(boss_csk_angle / 2))
hole_depth = boss_height + 0.1

for x, y in [(plate_width/2 - boss_size/2, plate_depth/2 - boss_size/2),
             (-plate_width/2 + boss_size/2, plate_depth/2 - boss_size/2),
             (-plate_width/2 + boss_size/2, -plate_depth/2 + boss_size/2),
             (plate_width/2 - boss_size/2, -plate_depth/2 + boss_size/2)]:
    boss = Pos(x, y, plate_thickness - 0.1 + boss_height/2) * Box(boss_size, boss_size, boss_height)
    result = result + boss
    cyl = Pos(x, y, plate_thickness - 0.1 + boss_height - hole_depth/2) * Cylinder(boss_hole_diameter/2, hole_depth)
    result = result - cyl
    cone = Pos(x, y, plate_thickness - 0.1 + boss_height - csk_height/2) * Cone(0, csk_radius, csk_height)
    result = result - cone

top_faces = result.faces().filter_by(Axis.Z)
top_edges = []
for f in top_faces:
    if f.center().Z > 0:
        top_edges.extend(f.edges())
result = chamfer(top_edges, chamfer_size)

part = result
part.name = "plate_with_pockets_slots_bosses"
export_step(part, "output.step")