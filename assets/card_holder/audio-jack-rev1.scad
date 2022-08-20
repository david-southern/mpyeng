include <BOSL/constants.scad>
use <BOSL/shapes.scad>
use <BOSL/transforms.scad>
use <BOSL/paths.scad>
use <BOSL/metric_screws.scad>

use <lazy.scad>
use <rounded_collar.scad>

$fn = 89;

show_jack = false;
laser_cut = true;

difference_fudge = 0.01;
extrusion_fudge = 0.1;
wall_thickness = 2;

barrel_diam = 9.4;
barrel_height = 1.8;  // This is the "remaining" barrel height after the retaining nut and washer are accounted for, assuming 3mm of support board thickness
nut_height = 2.2; // This is the height of the retaining nut above the support board
nut_width = 12; // This is the side-to-side width of the hex-nut
nut_radius = (nut_width / 2) / sin(60);

hex_cutout = false;
nut_ring_diam = 14;

// Extra amount to allow collar to fit over the nut
nut_fudge_x = 0.15;
nut_fudge_y = 0.4;

profile_height = barrel_height + 1;
profile_base_width = barrel_diam / 2;
profile_top_width = barrel_diam / 4;
profile_tight_corner = 0.5;
profile_wide_corner = 0.75;
profile_shoulder_height = nut_height;

if(laser_cut) {
    projection() jack_collar();
} else {
    jack_collar();
}

module jack_collar()
{
    zflip()
    difference()
    {
        audio_jack_collar();

        if(hex_cutout) {
            color("silver")
            tz(-difference_fudge)
            linear_extrude(height = nut_height + nut_fudge_y)
            polygon(path2d_regular_ngon(n=6, r=nut_radius + nut_fudge_x));
        } else {
            color("silver")
            tz(-difference_fudge)
            zcyl(l = nut_height, d=nut_ring_diam, align=ALIGN_POS);
        }
    }
}

if(show_jack)
{
    audio_jack();
}

module audio_jack()
{
    color("silver")
    linear_extrude(height = nut_height)
    polygon(path2d_regular_ngon(n=6, r=nut_radius));
    color("silver")
    zcyl(l = nut_height + barrel_height, d=barrel_diam, align=ALIGN_POS);
}

module audio_jack_collar() {
    circle_collar(interior_diameter=barrel_diam, 
        top_width=profile_top_width, base_width=profile_base_width,
        collar_height=profile_height, shoulder_height=profile_shoulder_height,
        inner_radius=profile_tight_corner, 
        outer_radius=profile_wide_corner, 
        shoulder_radius=profile_tight_corner,
        circle_qual=27, profile_qual=11);
}