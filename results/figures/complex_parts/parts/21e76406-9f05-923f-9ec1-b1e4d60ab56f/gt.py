from build123d import *

total_width = 80.0
vertical_height = 70.0
bracket_thickness = 6.0
rib_base_width = 12.0
rib_top_width = 4.0
rib_height = 45.0
rib_thickness = 3.0
fillet_radius = 2.0
hole_diameter = 5.0
cbore_diameter = 7.5
cbore_depth = 2.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Line((0, 0), (total_width, 0))
            Line((total_width, 0), (total_width, bracket_thickness))
            Line((total_width, bracket_thickness), (bracket_thickness, bracket_thickness))
            Line((bracket_thickness, bracket_thickness), (bracket_thickness, vertical_height))
            Line((bracket_thickness, vertical_height), (0, vertical_height))
            Line((0, vertical_height), (0, 0))
        make_face()
    extrude(amount=bracket_thickness)

solid_body = p.part
solid_body = fillet(solid_body.edges().filter_by(Axis.Z), fillet_radius)

face_cy, face_cz = vertical_height / 2, bracket_thickness / 2
with BuildPart() as pr:
    with BuildSketch(Plane.YZ) as sr:
        with BuildLine() as blr:
            Line((0, 0), (rib_base_width, 0))
            Line((rib_base_width, 0), (rib_top_width, rib_height))
            Line((rib_top_width, rib_height), (0, rib_height))
            Line((0, rib_height), (0, 0))
        make_face()
    extrude(amount=-rib_thickness)
solid_body = solid_body + Pos(0, face_cy, face_cz) * pr.part

for x, y in [(total_width/3, bracket_thickness/2), (2*total_width/3, bracket_thickness/2),
             (bracket_thickness/2, vertical_height/3), (bracket_thickness/2, 2*vertical_height/3)]:
    solid_body = solid_body - Pos(x, y, bracket_thickness) * CounterBoreHole(hole_diameter/2, cbore_diameter/2, cbore_depth)

part = solid_body
part.name = "L_Mount_Bracket"
export_step(part, OUTPUT_PATH)