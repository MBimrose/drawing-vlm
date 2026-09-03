from build123d import *

plate_width = 80.0
plate_height = 40.0
plate_thickness = 5.0
flange_width = 30.0
flange_height = 60.0
boss_radius = 12.0
boss_height = 12.0
boss_hole_diameter = 8.0
chamfer_size = 1.0
mount_hole_diameter = 6.0
mount_hole_spacing = 50.0
slot_width = 10.0
slot_height = 20.0
rib_thickness = 3.0
rib_height = plate_height

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline(
                (-plate_width/2, -plate_height/2),
                (plate_width/2, -plate_height/2),
                (plate_width/2, plate_height/2),
                (flange_width/2, plate_height/2),
                (flange_width/2, plate_height/2 + flange_height),
                (-flange_width/2, plate_height/2 + flange_height),
                (-flange_width/2, plate_height/2),
                (-plate_width/2, plate_height/2),
                close=True
            )
        make_face()
    extrude(amount=plate_thickness)

solid_body = p.part

for x in [-mount_hole_spacing/2, mount_hole_spacing/2]:
    solid_body = solid_body - Pos(x, 0, 0) * Cylinder(mount_hole_diameter/2, 100)

solid_body = solid_body - Pos(plate_width/2, 0, 0) * Box(slot_width, slot_height, 100)

rib = Pos(-plate_width/2 + rib_thickness/2, 0, plate_thickness/2) * Box(rib_thickness, rib_height, plate_thickness)
solid_body = solid_body + rib

boss_center_y = plate_height/2 + flange_height/2
boss = Pos(0, boss_center_y, plate_thickness + boss_height/2) * Cylinder(boss_radius, boss_height)
solid_body = solid_body + boss

boss_hole = Pos(0, boss_center_y, plate_thickness + boss_height/2) * Cylinder(boss_hole_diameter/2, boss_height + 10)
solid_body = solid_body - boss_hole

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = chamfer(top_face.edges(), chamfer_size)

part = solid_body
part.name = "L_bracket_with_boss"
export_step(part, "output.step")