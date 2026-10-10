from build123d import *

plate_width = 80.0
plate_height = 60.0
plate_thickness = 5.0
rib_width = 20.0
rib_height = 30.0
hole_diameter = 6.0
countersink_diameter = 12.0
countersink_angle = 82.0
hole_offset = 25.0
chamfer_size = 0.8
relief_hole_dia = 3.0
relief_spacing = 10.0
edge_rib_thickness = 3.0
edge_rib_height = 8.0
edge_rib_width = 10.0

with BuildPart() as p:
    with BuildSketch() as s:
        Rectangle(plate_width, plate_height)
    extrude(amount=plate_thickness)
    base = p.part
    z_edges = base.edges().filter_by(Axis.Z)
    base = chamfer(z_edges, chamfer_size)

central_rib = Pos(0, 0, plate_thickness) * Box(rib_width, rib_width, rib_height)
base = base + central_rib

edge_rib_w = plate_width - 2*edge_rib_thickness
edge_rib_h = edge_rib_width
edge_rib_top = Pos(0, plate_height/2 - edge_rib_width/2, plate_thickness) * Box(edge_rib_w, edge_rib_h, edge_rib_height)
edge_rib_bottom = Pos(0, -plate_height/2 + edge_rib_width/2, plate_thickness) * Box(edge_rib_w, edge_rib_h, edge_rib_height)
base = base + edge_rib_top + edge_rib_bottom

z_top = plate_thickness + rib_height
csk_depth = plate_thickness + rib_height

for dx in (-hole_offset, hole_offset):
    for dy in (-hole_offset, hole_offset):
        csk = Pos(dx, dy, z_top) * Rot(180, 0, 0) * CounterSinkHole(hole_diameter/2, countersink_diameter/2, csk_depth, countersink_angle)
        base = base - csk

num_x = int((plate_width - 2 * relief_spacing) // relief_spacing)
num_y = int((plate_height - 2 * relief_spacing) // relief_spacing)
relief_depth = z_top + 10.0

for i in range(num_x):
    for j in range(num_y):
        x = -plate_width/2 + relief_spacing + i * relief_spacing
        y = -plate_height/2 + relief_spacing + j * relief_spacing
        if abs(x) < rib_width/2 + 2 and abs(y) < rib_width/2 + 2:
            continue
        relief = Pos(x, y, z_top) * Cylinder(relief_hole_dia/2, relief_depth)
        base = base - relief

part = base
part.name = "plate_with_ribs_and_holes"
export_step(part, OUTPUT_PATH)