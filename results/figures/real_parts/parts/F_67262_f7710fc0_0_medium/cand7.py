from build123d import *

plate_length = 80.0
plate_width = 32.0
plate_thickness = 8.0
boss_radius = 8.0
boss_height = 32.0
boss_offset = 12.0
central_hole_diameter = 12.0
chamfer_distance = 1.0

with BuildPart() as p:
    with BuildSketch() as s:
        SlotOverall(plate_length, plate_width)
    extrude(amount=plate_thickness)

solid_body = p.part

boss1 = Pos(-plate_length/2 + boss_offset, 0, plate_thickness/2 + boss_height/2) * Cylinder(boss_radius, boss_height)
boss2 = Pos(plate_length/2 - boss_offset, 0, plate_thickness/2 - boss_height/2) * Cylinder(boss_radius, boss_height)

solid_body = solid_body + boss1 + boss2

hole = Pos(0, 0, plate_thickness/2) * Cylinder(central_hole_diameter/2, plate_thickness + 2)
solid_body = solid_body - hole

vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = chamfer(vertical_edges, chamfer_distance)

part = solid_body
part.name = "plate_with_bosses"
export_step(part, "output.step")