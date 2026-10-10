from build123d import *

liner_inner_radius = 30.0
liner_thickness = 5.0
liner_length = 80.0
bottom_thickness = liner_thickness
pocket_radius = 15.0
pocket_depth = 20.0
chamfer_dist = 2.0
tab_thickness = 3.0
tab_width = 12.0
tab_height = 8.0
tab_count = 6
slot_width = 4.0
slot_depth = 2.5
slot_spacing = 12.0
slot_count = 4

outer_radius = liner_inner_radius + liner_thickness

with BuildPart() as p:
    with BuildSketch() as s:
        Circle(outer_radius)
    extrude(amount=liner_length)

solid_body = p.part

pocket = Pos(0, 0, bottom_thickness) * Cylinder(pocket_radius, pocket_depth)
solid_body = solid_body - pocket

inner_cav = Pos(0, 0, bottom_thickness) * Cylinder(liner_inner_radius, liner_length - bottom_thickness)
solid_body = solid_body - inner_cav

for i in range(tab_count):
    angle = i * 360.0 / tab_count
    tab = Rot(0, 0, angle) * Pos(outer_radius - tab_thickness/2, 0, liner_length/2) * Box(tab_thickness, tab_width, tab_height)
    solid_body = solid_body + tab

for i in range(slot_count):
    angle = i * 360.0 / slot_count
    slot = Rot(0, 0, angle) * Pos(outer_radius - slot_depth/2, 0, liner_length/2) * Box(slot_depth, slot_width, liner_length - 2*slot_spacing)
    solid_body = solid_body - slot

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
top_edges = top_face.edges()
solid_body = chamfer(top_edges, chamfer_dist)

part = solid_body
part.name = "liner_with_tabs"
export_step(part, OUTPUT_PATH)