from build123d import *
case_length = 80.0
case_width = 50.0
case_height = 20.0
wall_thickness = 2.0
spreader_thickness = 2.0
spreader_margin = 4.0
spreader_length = case_length - 2*spreader_margin
spreader_width = case_width - 2*spreader_margin
through_hole_diameter = 1.5
through_hole_grid_length = 60.0
through_hole_grid_width = 30.0
through_hole_spacing_x = 10.0
through_hole_spacing_y = 10.0
mount_hole_diameter = 3.0
chamfer_distance = 0.8
rib_thickness = 2.0
rib_height = case_height - 2*wall_thickness - spreader_thickness
with BuildPart() as p:
    with BuildSketch() as s:
        Rectangle(case_length, case_width)
    extrude(amount=case_height)
solid = p.part
top_face = solid.faces().sort_by(Axis.Z)[-1]
bottom_face = solid.faces().sort_by(Axis.Z)[0]
solid = offset(solid, amount=-wall_thickness, openings=[top_face, bottom_face])
spreader = Pos(0, 0, wall_thickness + spreader_thickness/2) * Box(spreader_length, spreader_width, spreader_thickness)
solid = solid + spreader
rib_offset = (case_width/2) - wall_thickness - rib_thickness/2
rib1 = Pos(0, rib_offset, wall_thickness + spreader_thickness + rib_height/2) * Box(case_length - 2*wall_thickness, rib_thickness, rib_height)
rib2 = Pos(0, -rib_offset, wall_thickness + spreader_thickness + rib_height/2) * Box(case_length - 2*wall_thickness, rib_thickness, rib_height)
solid = solid + rib1 + rib2
hole_cols = int(through_hole_grid_length/through_hole_spacing_x) + 1
hole_rows = int(through_hole_grid_width/through_hole_spacing_y) + 1
for i in range(hole_cols):
    for j in range(hole_rows):
        x = -through_hole_grid_length/2 + i * through_hole_spacing_x
        y = -through_hole_grid_width/2 + j * through_hole_spacing_y
        hole = Pos(x, y, case_height/2) * Cylinder(through_hole_diameter/2, case_height + 10)
        solid = solid - hole
solid = solid - Pos(case_length/2, 0, case_height/2) * Rot(0, 90, 0) * Cylinder(mount_hole_diameter/2, case_length + 10)
solid = solid - Pos(-case_length/2, 0, case_height/2) * Rot(0, 90, 0) * Cylinder(mount_hole_diameter/2, case_length + 10)
outer_faces = [f for f in solid.faces() if abs(f.normal_at().X) > 0.9 or abs(f.normal_at().Y) > 0.9 or abs(f.normal_at().Z) > 0.9]
outer_edges = [e for f in outer_faces for e in f.edges()]
solid = chamfer(outer_edges, chamfer_distance)
part = solid
part.name = "electronic_enclosure"
export_step(part, OUTPUT_PATH)