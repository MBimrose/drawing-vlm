from build123d import *

knob_outer_radius = 30.0
knob_height = 45.0
ridge_height = 10.0
ridge_inner_radius = 22.0
base_radius = 28.0
through_hole_diameter = 10.0
top_chamfer = 2.0
slot_width = 8.0
slot_fillet = 0.5

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            Polyline((base_radius, 0), (base_radius, knob_height - ridge_height),
                     (ridge_inner_radius, knob_height - ridge_height),
                     (ridge_inner_radius, knob_height),
                     (0, knob_height), (0, 0), close=True)
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part
solid_body = solid_body - Cylinder(through_hole_diameter / 2, knob_height)

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = chamfer(top_face.edges(), top_chamfer)

slot_cutter = Pos(knob_outer_radius - slot_width / 2, 0, knob_height / 2) * Box(slot_width, knob_height, 2 * knob_outer_radius)
solid_body = solid_body - slot_cutter

solid_body = fillet(solid_body.edges().filter_by(Axis.Z), slot_fillet)

part = solid_body
part.name = "knob"
export_step(part, OUTPUT_PATH)