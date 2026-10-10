from build123d import *

shaft_diameter = 20.0
collar_outer_diameter = 40.0
collar_length = 70.0
shoulder_length = 10.0
step_outer_diameter = 30.0
step_length = 15.0
keyseat_width = 8.0
keyseat_depth = 4.0
set_screw_diameter = 4.0
set_screw_margin = 2.0
chamfer_distance = 2.0

R_shaft = shaft_diameter / 2.0
R_outer = collar_outer_diameter / 2.0
R_step = step_outer_diameter / 2.0

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            Polyline((R_outer, 0), (R_outer, shoulder_length), (R_step, shoulder_length),
                     (R_step, shoulder_length + step_length), (R_outer, shoulder_length + step_length),
                     (R_outer, collar_length), (R_shaft, collar_length), (R_shaft, 0), close=True)
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part
chamfer_edges = solid_body.faces().sort_by(Axis.Z)[0].edges()
solid_body = chamfer(chamfer_edges, chamfer_distance)

x_pos = R_outer - set_screw_margin - set_screw_diameter / 2.0
z_pos = collar_length / 2.0
hole_tool = Pos(x_pos, 0, z_pos) * Rot(0, 90, 0) * Cylinder(set_screw_diameter / 2, collar_length)
solid_body = solid_body - hole_tool

keyseat_tool = Pos(R_shaft, 0, collar_length / 2) * Box(keyseat_depth, keyseat_width, collar_length)
solid_body = solid_body - keyseat_tool

part = solid_body
part.name = "collar_shaft"
export_step(part, OUTPUT_PATH)