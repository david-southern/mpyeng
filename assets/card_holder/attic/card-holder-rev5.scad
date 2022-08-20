include <BOSL/constants.scad>
use <BOSL/shapes.scad>
use <BOSL/transforms.scad>

$fn=37;

difference_fudge = 0.1;
extrusion_fudge = 0.1;

acrylic_thickness = 3.25;

mag_diam = 8 + extrusion_fudge * 2;
mag_thickness = 3 - extrusion_fudge;

frame_xside_width = 12;
frame_yside_width = 14;
frame_extra_thickness = 3;
mag_frame_offset = 4;
acrylic_depth = 2;

frame_overlap = 2;

card_width = 54;
card_height = 81;
card_thickness = acrylic_thickness;

frame_width = card_width + (frame_xside_width - frame_overlap) * 2;
frame_height = card_height+ (frame_yside_width - frame_overlap) * 2;
frame_depth = frame_extra_thickness + acrylic_thickness;
corner_fillet = 2;

zflip()
{
    frame();

    translate([frame_width, 0, 0])
    snap();

    translate([-frame_width * 1.25, 0, 0])
    back_frame();
}

module frame()
{
    spread_height = frame_height - mag_diam - mag_frame_offset;
    spread_width = frame_width - mag_diam - mag_frame_offset;

    difference()
    {
        color("blue")
        cuboid([frame_width, frame_height, frame_depth], fillet=corner_fillet);
        
        color("magenta")
        cuboid([
            card_width - frame_overlap * 2, 
            card_height - frame_overlap * 2, 
            frame_depth * 2
        ], fillet=corner_fillet);
        
        color("yellow")
        translate([0, 0, -frame_depth + frame_depth / 2 - acrylic_depth])
        cuboid([
            card_width, 
            card_height, 
            frame_depth * 2
        ]);
       
        color("silver")
        translate([0, 0, -(frame_depth - mag_thickness + difference_fudge) / 2])
        {
            translate([0, spread_height / 2, 0])
            xspread(spacing=spread_width, l=spread_width) {
                cyl(l=mag_thickness +  + difference_fudge, d=mag_diam);
            }
            
            translate([0, -spread_height / 2, 0])
            xspread(spacing=spread_width / 6, l=spread_width) {
                cyl(l=mag_thickness + difference_fudge, d=mag_diam);
            }
           
        }
    }
}

module snap()
{
    intersection()
    {
        difference() {
            color("blue")
            cuboid([frame_width, frame_height, frame_depth], fillet=corner_fillet);
            
            color("magenta")
            cuboid([
                card_width - frame_overlap * 2, 
                card_height - frame_overlap * 2, 
                frame_depth * 2
            ], fillet=corner_fillet);
        }
        
        color("yellow")
        translate([0, 0, 
            -frame_depth + frame_depth / 2 - acrylic_depth - acrylic_thickness])
        cuboid([
            card_width, 
            card_height, 
            frame_depth * 2
        ]);
        
    }
}

module back_frame()
{
    spread_height = frame_height - mag_diam - mag_frame_offset;
    spread_width = frame_width - mag_diam - mag_frame_offset;

    bottom_half(z=-frame_depth / 2 + mag_thickness + acrylic_depth, s=frame_height * 1.5)
    difference()
    {
        color("blue")
        cuboid(
            [frame_width, frame_height, frame_depth], 
            fillet=corner_fillet, edges=EDGES_Z_ALL);
        
        color("yellow")
        cuboid([
            card_width, 
            card_height, 
            frame_depth * 2
        ]);
       
        color("silver")
        translate([0, 0, -(frame_depth - mag_thickness + difference_fudge) / 2])
        {
            translate([0, spread_height / 2, 0])
            xspread(spacing=spread_width, l=spread_width) {
                cyl(l=mag_thickness +  + difference_fudge, d=mag_diam);
            }
            
            translate([0, -spread_height / 2, 0])
            xspread(spacing=spread_width, l=spread_width) {
                cyl(l=mag_thickness + difference_fudge, d=mag_diam);
            }
           
            translate([0, -spread_height / 2, 0])
            xspread(spacing=spread_width / 6, l=spread_width * 2 / 3) {
                cuboid([mag_diam, mag_diam * 2, mag_thickness + difference_fudge]);
            }
           
        }
    }
}


module card()
{
    color("red")
    cuboid([card_width, card_height, card_thickness]);
}
