include <BOSL2/std.scad>
include <BOSL2/shapes3d.scad>
include <useful_stuff.scad>

audio_jack_color = "steelblue";

/* [Print Properties] */
show_jack = false;
show_jack_mock = false;

/* [Jack Properties] */
// How far does the top of the collar extend beyond the end of the jack's barrel, in mm
profile_height_above_barrel_end = 1; // 0.01

// The diameter of the bottom of the collar, as a percentage of the barrel diameter
profile_bottom_diam_pct = 200; // [100:0.5:500]

// The percentage ratio of the top width of the collar to the bottom width
profile_top_pct = 50; // [10:0.5:100]

// Percentage of the barrel top width used for edge fillet
profile_top_fillet_pct = 43; // [0:0.5:100]

// Height of the 'straight' portion of the collar that maintains the bottom barrel diam before
// narrowing to the top diam, to accommodate the retaining nut, as a percentage of the retaining nut
// thickness
profile_shoulder_height_pct = 100; // [100:0.5:500]

// Extra amount to punch out of the collar to allow it to fit over the nut
nut_fudge = 0.4;

/* [Hidden] */
// These are the physical dimensions of the 1/4" audio jacks we are using

// Diameter of the threaded barrel portion of the audio jack
barrel_diam = 9.4;
// This is the "remaining" barrel height that protrudes through the eng panel support board
barrel_height = 3.5;

nut_height = 1.75; // This is the height of the retaining nut above the support board
nut_width = 12; // This is the side-to-side width of the hex-nut
hex_cutout = false;

nut_radius = (nut_width / 2) / sin(60);

audio_jack_collar_depth = barrel_height + profile_height_above_barrel_end;
audio_jack_collar_diameter = barrel_diam * toPct(profile_bottom_diam_pct);
bottom_width = (audio_jack_collar_diameter - barrel_diam) / 2;
profile_top_width = bottom_width * toPct(profile_top_pct);
profile_top_diam = barrel_diam + profile_top_width * 2;
profile_shoulder_height = nut_height * toPct(profile_shoulder_height_pct);
profile_cone_height = audio_jack_collar_depth - profile_shoulder_height;
profile_top_rounding = profile_top_width * toPct(profile_top_fillet_pct);

if(show_jack)
{
    audio_jack_collar();
}

module audio_jack_collar(anchor=CENTER, spin=0, orient=UP)
{
    attachable(anchor, spin, orient, size=[audio_jack_collar_diameter, audio_jack_collar_diameter, audio_jack_collar_depth])
    {
        render()
        difference()
        {
            collar_blank(anchor=BOTTOM);
            down(epsilon)
            audio_jack_punch(anchor=BOTTOM);
        }
        children();
    }
}

if(show_jack_mock)
{
    audio_jack_mock(anchor=BOTTOM);
}

module collar_blank(anchor=CENTER, spin=0, orient=UP)
{
    attachable(anchor, spin, orient, size=[audio_jack_collar_diameter, audio_jack_collar_diameter, audio_jack_collar_depth]) {
        color(audio_jack_color)
        union()
        {
            down(audio_jack_collar_depth / 2)
            cyl(
                l = profile_shoulder_height,
                d = audio_jack_collar_diameter,
                anchor = BOTTOM
            )
            position(TOP)
            cyl(
                l = profile_cone_height,
                d1 = audio_jack_collar_diameter,
                d2 = profile_top_diam,
                rounding2 = profile_top_rounding,
                anchor = BOTTOM
            );
        }
        children();
    }
}

module audio_jack_punch(anchor=CENTER, spin=0, orient=UP)
{
    punch_height = audio_jack_collar_depth + epsilon * 2;
    punch_width = nut_radius * 2 + nut_fudge * 2;
    attachable(anchor, spin, orient, size=[punch_width, punch_width, punch_height]) {
        color(audio_jack_color)
        {
            cyl(l = punch_height, d = barrel_diam, rounding2 = -profile_top_rounding, anchor=CENTER)
            align(BOTTOM, inside=true)
            cyl(l = nut_height + nut_fudge, d = punch_width, anchor=BOTTOM);
        }
        children();
    }
}

module audio_jack_mock(anchor=CENTER, spin=0, orient=UP)
{
    attachable(anchor, spin, orient, size=[nut_radius * 2, nut_radius * 2, barrel_height]) {
        color("silver")
        {
            cyl(l = barrel_height, d = barrel_diam, anchor=CENTER)
            align(BOTTOM, inside=true)
            cyl(l = nut_height, r = nut_radius, anchor=BOTTOM, $fn = 6);
        }
        children();
    }
}