from build123d import *

plate_length = 80.0
plate_width = 60.0
plate_thickness = 6.0
boss_radius = 8.0
boss_height = 12.0
slot_length = 20.0
slot_width = 5.0
slot_offset = 30.0
hole_diameter = 3.2
hole_offset = 10.0
chamfer_distance = 1.0

with BuildPart() as p:
    with BuildSketch() as s:
        Rectangle(plate_length, plate_width)
    extrude(amount=plate_thickness)

solid_body = p.part

slot_box = Pos(slot_offset, 0, plate_thickness/2) * Box(slot_length, slot_width, plate_thickness)
solid_body = solid_body - slot_box

boss_cyl = Pos(0, 0, plate_thickness) * Cylinder(boss_radius, boss_height)
solid_body = solid_body + boss_cyl

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
top_edges = top_face.edges()
solid_body = chamfer(top_edges, chamfer_distance)

hole_positions = [
    (hole_offset, hole_offset),
    (plate_length - hole_offset, hole_offset),
    (hole_offset, plate_width - hole_offset),
    (plate_length - hole_offset, plate_width - hole_offset)
]
for x, y in hole_positions:
    hole = Pos(x, y, plate_thickness/2) * Cylinder(hole_diameter/2, plate_thickness + 2)
    solid_body = solid_body - hole

part = solid_body
part.name = "plate_with_boss_and_holes"
export_step(part, "output.step")