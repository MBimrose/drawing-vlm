from build123d import *
import math

plate_width = 80.0
plate_height = 60.0
plate_thickness = 5.0
tab_width = 20.0
tab_height = 10.0
slot_width = 30.0
slot_height = 12.0
hole_diameter = 5.5
hole_circle_radius = 20.0
chamfer_size = 0.8

with BuildPart() as p:
    with BuildSketch() as s:
        Rectangle(plate_width, plate_height)
    extrude(amount=plate_thickness)

solid_body = p.part
tab = Pos(0, -plate_height/2 - tab_height/2, plate_thickness/2) * Box(tab_width, tab_height, plate_thickness)
solid_body = solid_body + tab

vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = chamfer(vertical_edges, chamfer_size)

slot = Pos(0, 0, plate_thickness/2) * Box(slot_width, slot_height, plate_thickness)
solid_body = solid_body - slot

for i in range(6):
    angle = math.radians(i * 360.0 / 6)
    px = hole_circle_radius * math.cos(angle)
    py = hole_circle_radius * math.sin(angle)
    hole = Pos(px, py, plate_thickness/2) * Cylinder(hole_diameter/2, plate_thickness)
    solid_body = solid_body - hole

part = solid_body
part.name = "plate_with_tab_and_holes"
export_step(part, "output.step")