from build123d import *
import math

plate_width = 80.0
plate_height = 50.0
plate_thickness = 10.0
tab_width = 30.0
tab_height = 10.0
slot_width = 30.0
slot_height = 6.0
slot_offset_y = 5.0
hole_diameter = 4.5
hole_head_diameter = 8.6
hole_head_angle = 90
hole_spacing = 50.0
chamfer_size = 0.8

with BuildPart() as p:
    with BuildSketch() as s:
        Rectangle(plate_width, plate_height)
        Pos(0, plate_height/2 + tab_height/2, 0) * Rectangle(tab_width, tab_height)
    extrude(amount=plate_thickness)

solid_body = p.part

slot_cut = Pos(0, slot_offset_y, plate_thickness/2) * Box(slot_width, slot_height, plate_thickness)
solid_body = solid_body - slot_cut

csk_radius = hole_head_diameter / 2
csk_height = csk_radius / math.tan(math.radians(hole_head_angle / 2))
bore_radius = hole_diameter / 2

for x in [-hole_spacing/2, hole_spacing/2]:
    bore = Pos(x, 0, plate_thickness/2) * Cylinder(bore_radius, plate_thickness)
    solid_body = solid_body - bore
    csk = Pos(x, 0, csk_height/2) * Cone(csk_radius, 0, csk_height)
    solid_body = solid_body - csk

vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = chamfer(vertical_edges, chamfer_size)

part = solid_body
part.name = "wall_mount_plate"
export_step(part, "output.step")