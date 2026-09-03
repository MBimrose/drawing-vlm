from build123d import *

beam_length = 80.0
beam_height = 80.0
flange_width = 40.0
flange_thickness = 5.0
web_thickness = 5.0
shell_thickness = 2.0
notch_width = 3.0
notch_height = 10.0
notch_depth = 2.0
notch_spacing = 12.0
num_notches = int((beam_height - 2 * flange_thickness) // notch_spacing)

pts = [
    (0, -beam_height/2),
    (flange_width/2, -beam_height/2),
    (flange_width/2, -beam_height/2 + flange_thickness),
    (web_thickness/2, -beam_height/2 + flange_thickness),
    (web_thickness/2, beam_height/2 - flange_thickness),
    (flange_width/2, beam_height/2 - flange_thickness),
    (flange_width/2, beam_height/2),
    (0, beam_height/2)
]

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            Polyline(*pts, close=True)
        make_face()
        mirror(about=Plane.YZ)
    extrude(amount=beam_length)

solid_body = p.part
solid_body = offset(solid_body, amount=-shell_thickness)

for i in range(num_notches):
    z_pos = -beam_height/2 + flange_thickness + notch_spacing/2 + i * notch_spacing
    notch = Pos(web_thickness/2 - notch_depth/2, 0, z_pos) * Box(notch_depth, beam_length, notch_height)
    solid_body = solid_body - notch

part = solid_body
part.name = "I-beam_with_notches"
export_step(part, "output.step")