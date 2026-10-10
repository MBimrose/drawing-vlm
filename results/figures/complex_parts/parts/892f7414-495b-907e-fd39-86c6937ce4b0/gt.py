from build123d import *

leaf_length = 80.0
leaf_width = 30.0
leaf_thickness = 8.0
bore_diameter = 10.0
shoulder_length = 15.0
shoulder_thickness = 4.0
rib_count = 4
rib_width = 2.0
rib_depth = 3.0
fillet_radius = 0.5
edge_clearance = 2.0

base = Box(leaf_length, leaf_width, leaf_thickness)

shoulder_cx = -leaf_length/2 + shoulder_length/2
shoulder_cz = -leaf_thickness + shoulder_thickness/2
shoulder = Pos(shoulder_cx, 0, shoulder_cz) * Box(shoulder_length, leaf_width, shoulder_thickness)

result = base + shoulder

rib_spacing = (leaf_width - rib_count * rib_width) / (rib_count + 1)
rib_positions = [
    -leaf_width/2 + rib_spacing * (i + 1) + rib_width * i + rib_width/2
    for i in range(rib_count)
]

rib_x_start = shoulder_cx + shoulder_length/2
rib_z_center = shoulder_cz

for y_pos in rib_positions:
    rib = Pos(rib_x_start + rib_depth/2, y_pos, rib_z_center) * Box(rib_depth, rib_width, leaf_width - 2*edge_clearance)
    result = result + rib

sorted_faces = result.faces().sort_by(Axis.Z)
max_z = sorted_faces[-1].center().Z
top_edges = []
for f in result.faces():
    if f.center().Z > max_z - 0.1:
        top_edges.extend(f.edges())
result = fillet(top_edges, fillet_radius)

hole = Cylinder(bore_diameter/2, 200)
result = result - hole

part = result
part.name = "leaf_with_ribs_and_hole"
export_step(part, OUTPUT_PATH)