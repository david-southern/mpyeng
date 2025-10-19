include <BOSL2/std.scad>
use <lazy.scad>

/* [Rendering Options] */ 
RenderPieces = 7; // [1: Main Tray, 2: Lock Bars, 4: Strip Supports, 7: All, 0: None]
FlipTray = true;
Debug = false;

/* [Print Settings] */ 
printer_fudge = 0.15;

/* [Main Tray] */ 
card_tray_width = 90;
card_tray_height = 120;
card_rim_thickness = 9;
card_wall_width = 7;
card_waist_height = 70;

pixel_grid_size = 5;
pixel_size_mm = 5;
pixel_cell_depth = 1.7;
// How far the top of a pixel is inset from the surface of the tray. Also affects the thickness of
// the tray at the lock bar joint cutouts on the edge of the tray.
pixel_cell_inset = 1;

/* [Lock Bars] */ 
bend_bar_arc_height = 2;
lock_bar_height = 3;
lock_sphere_diameter = 2;
lock_bar_width = card_tray_width - card_wall_width * 2;

/* [Magnets/Supports] */ 
magnet_height = 3;
magnet_diameter = 8;
magnet_hole_diameter = magnet_diameter + printer_fudge * 2;
magnet_inset_depth = 0.8;

support_post_wire_hole_diameter = "26AWG"; // [22AWG, 26AWG]

/* [Hidden] */ 
// Parameters defined in this section are hidden from the Customizer
$fn = 43;

card_tray_thickness = pixel_cell_depth + pixel_cell_inset;
pixel_cell_size = pixel_size_mm + printer_fudge * 2;

strip_width = 10;
// Size/spacing of the solder pads on the strip
strip_pin_width = 1.7;
strip_pin_spacing = 3;

// Pixel cell distance from center to center
pixel_cell_spacing = 13;
// Amount of strip between two pixels
intra_pixel_spacing = 11.5;

intra_cell_spacing = pixel_cell_spacing - pixel_cell_size - printer_fudge * 4;
max_pixel_cell_spacing = pixel_cell_size + intra_pixel_spacing;

echo(str("Pixel Cell Spacing: ", pixel_cell_spacing));
echo(str("Intra Cell Spacing: ", intra_cell_spacing));

assert(pixel_cell_spacing <= max_pixel_cell_spacing, 
    str("Pixel Cell Spacing (", pixel_cell_spacing, ") must be less than or equal to Pixel Cell Size + Intra Pixel Spacing (", max_pixel_cell_spacing, ")"
    )
);

// If the intra_cell_spacing is less than the intra_pixel_spacing, then the strip cannot lay flat
// against the back of the card tray. In this case, create 'bend arcs' between pixel cells so that
// the strip can lay flat against the back of the bend arcs and not have to be bent to conform to
// the intra_cell_spacing.
//
// Note: Per this discussion: https://math.stackexchange.com/a/4411391 it is not possible to
// calculate the sagitta (height) of an arc given only the chord length and arc height. The
// stackexchange post gives a formula for a "good enough" approximation which is used here. Note:
// for this calculation, the arg length and chord length are the *full* lengths - most other
// calculations use half lengths.
arc_length = intra_pixel_spacing; // 11.5
chord_length = intra_cell_spacing; // 7
bend_arc_sagitta = 0.42 * sqrt(arc_length ^ 2 - chord_length ^ 2);
// Now turn the sagitta and chord length into a radius for the circle needed to create the arc.
// Formula here: https://www.vcalc.com/wiki/vcalc/radius-of-circle-from-chord-length-and-arc-height
bend_bar_radius = chord_length ^ 2 / (8 * bend_arc_sagitta) + bend_arc_sagitta / 2;
bend_bar_resistor_cutout_width = 3;

echo(str("Arc Length: ", arc_length));
echo(str("Chord Length: ", chord_length));
echo(str("Bend Arc Sagitta: ", bend_arc_sagitta));
echo(str("Bend Bar Radius: ", bend_bar_radius));

strip_separator_width = pixel_cell_spacing - strip_width;

card_height = card_tray_height - card_wall_width;
card_width = card_tray_width - card_wall_width * 2;
card_waist_start = (card_height - card_waist_height - card_wall_width * 2) / 2;

card_tray_x_0 = 0; 
card_tray_x_1 = card_wall_width;
card_tray_x_2 = card_wall_width * 2;
card_tray_x_3 = card_tray_width - card_wall_width * 2;
card_tray_x_4 = card_tray_width - card_wall_width;
card_tray_x_5 = card_tray_width;

card_tray_y_0 = 0;
card_tray_y_1 = card_wall_width;
card_tray_y_2 = card_wall_width + card_waist_start;
card_tray_y_3 = card_wall_width + card_waist_start + card_wall_width;
card_tray_y_4 = card_wall_width + card_waist_start + card_wall_width + card_waist_height;
card_tray_y_5 = card_wall_width + card_waist_start + card_wall_width + card_waist_height + card_wall_width;
card_tray_y_6 = card_tray_height;

epsilon = 0.01; // Small value to ensure proper subtraction

PIECES_MAIN_TRAY = 1;
PIECES_LOCK_BARS = 2;
PIECES_STRIP_SUPPORTS = 4;

wire_22ga_outer_diameter = 2.8;
wire_26ga_outer_diameter = 1.6;

wire_outer_diameter = support_post_wire_hole_diameter == "22AWG" ? wire_22ga_outer_diameter : wire_26ga_outer_diameter;
lock_bar_assy_color = "#999999";

function CheckRenderPieces(bit) = (RenderPieces & bit) == bit;

if (CheckRenderPieces(PIECES_MAIN_TRAY))
{
    echo(str("Rendering main tray pieces"));

    render()
    ry(FlipTray ? 180 : 0)
    {
        difference()
        {
            card_tray();

            lock_bars(punch=true);
        }

        lock_bar_assy();
    }
}

if (CheckRenderPieces(PIECES_LOCK_BARS))
{
    echo(str("Rendering lock bars"));
    tx(card_tray_width)
    tz(lock_bar_height)
    rz(90)
    lock_bars();
}

if (CheckRenderPieces(PIECES_STRIP_SUPPORTS))
{
    echo(str("Rendering strip supports"));
}

module flat_strip()
{
    strip_length = pixel_cell_spacing * pixel_grid_size;

    xcopies(intra_pixel_spacing, pixel_grid_size)
    {
        color("darkgray")
        cube([strip_width, strip_length, 0.2], anchor=BOTTOM);

        color("orange")
        xcopies(strip_pin_spacing, 3)
        cube([strip_pin_width, strip_length, 0.2 + epsilon], anchor=BOTTOM);
    }
}

function sum_vectors(vec_list, start = 0, end = len(vec_list) - 1, zero_value = [0, 0, 0]) =
    end < start ? zero_value :
    vec_list[start] + sum_vectors(vec_list, start + 1, end);

module card_tray()
{
    union()
    {
        difference()
        {
            tx(-card_tray_width/2)
            ty(-card_tray_height/2)
            {
                difference()
                {
                    card_outer_tray(card_tray_thickness);

                    // Inner tray
                    tz(-epsilon)
                    scale([1, 1, 10]) card_inner_tray();
                    tz(card_tray_thickness)
                    scale([1, 1, 10]) card_waist();
                }
                card_inner_tray();
            }

            // Magnet holes
            ty(card_wall_width / 2)
            xcopies(card_tray_width - card_wall_width * 4 - magnet_diameter / 2 * 0, 2)
            ycopies(card_tray_height - card_wall_width * 4 - magnet_diameter / 2 * 0, 2)
            cylinder(h=100, d=magnet_hole_diameter, center=true);

            pixel_grid();
        }

        // Board Support Posts
        ty(card_wall_width / 2)
        tz(card_tray_thickness - magnet_inset_depth)
        xcopies(card_tray_width - card_wall_width * 4 - magnet_diameter / 2 * 0, 2)
        ycopies(card_tray_height - card_wall_width * 4 - magnet_diameter / 2 * 0, 2)
        difference()
        {
            cylinder(h=card_tray_thickness, d=magnet_hole_diameter, anchor = TOP);
            if($idx == 0) {
                cylinder(h=card_tray_thickness * 3, d=wire_outer_diameter * 1.5, center=true);
            }
        }
    }
}

module card_waist()
{
    linear_extrude(height=card_tray_thickness)
    polygon([
        [card_tray_x_0, card_tray_y_3],
        [card_tray_x_5, card_tray_y_3],
        [card_tray_x_5, card_tray_y_4],
        [card_tray_x_0, card_tray_y_4]
    ]);
}

module card_inner_tray()
{
    linear_extrude(height=card_tray_thickness)
    polygon([
        [card_tray_x_1, card_tray_y_1],
        [card_tray_x_4, card_tray_y_1],
        [card_tray_x_4, card_tray_y_2],
        [card_tray_x_3, card_tray_y_3],
        [card_tray_x_3, card_tray_y_4],
        [card_tray_x_4, card_tray_y_5],
        [card_tray_x_4, card_tray_y_6],
        [card_tray_x_1, card_tray_y_6],
        [card_tray_x_1, card_tray_y_5],
        [card_tray_x_2, card_tray_y_4],
        [card_tray_x_2, card_tray_y_3],
        [card_tray_x_1, card_tray_y_2]
    ]);
}

module card_outer_tray(tray_depth = card_rim_thickness)
{
    linear_extrude(height=tray_depth)
    polygon([
        [card_tray_x_0, card_tray_y_0],
        [card_tray_x_2, card_tray_y_0],
        [card_tray_x_2, card_tray_y_1],
        [card_tray_x_3, card_tray_y_1],
        [card_tray_x_3, card_tray_y_0],
        [card_tray_x_5, card_tray_y_0],
        [card_tray_x_5, card_tray_y_2],
        [card_tray_x_4, card_tray_y_3],
        [card_tray_x_4, card_tray_y_4],
        [card_tray_x_5, card_tray_y_5],
        [card_tray_x_5, card_tray_y_6],
        [card_tray_x_0, card_tray_y_6],
        [card_tray_x_0, card_tray_y_5],
        [card_tray_x_1, card_tray_y_4],
        [card_tray_x_1, card_tray_y_3],
        [card_tray_x_0, card_tray_y_2]
    ]);
}

module pixel_grid() {
    color("pink")
    tz(-epsilon)
    xcopies(pixel_cell_spacing, pixel_grid_size)
    {
        ycopies(pixel_cell_spacing, pixel_grid_size)
        {
            cube([pixel_cell_size, pixel_cell_size, card_tray_thickness * 2], anchor=BOTTOM);
        }
    }
}

module lock_bar_assy()
{
    color(lock_bar_assy_color)
    difference()
    {
        // Grid Base
        cube([
            lock_bar_width,
            pixel_cell_spacing * pixel_grid_size + epsilon, 
            lock_bar_height + epsilon
        ], anchor=TOP);

        cube([
            pixel_cell_spacing * pixel_grid_size,
            pixel_cell_spacing * pixel_grid_size + epsilon,
            lock_bar_height + epsilon
        ], anchor = TOP);

        lock_bars(punch=true);

        ycopies(pixel_cell_spacing, pixel_grid_size)
        cube([
            pixel_cell_spacing * pixel_grid_size + epsilon,
            pixel_cell_size,
            lock_bar_height + epsilon
        ], anchor = TOP);

        ycopies(pixel_cell_spacing * pixel_grid_size, 2)
        cube([
            pixel_cell_spacing * pixel_grid_size + epsilon,
            pixel_cell_size,
            lock_bar_height + epsilon
        ], anchor = TOP);
    }
    
    color("red")
    xcopies(pixel_cell_spacing, pixel_grid_size)
    ycopies(pixel_cell_spacing, pixel_grid_size - 1)
    bend_arc();
}

module bend_arc()
{
    rz(90)
    rx(-90)
    ty(-(bend_bar_radius - bend_arc_sagitta))
    difference()
    {
        cylinder(r = bend_bar_radius, h = strip_width, center = true);
        ty(-bend_arc_sagitta)
        cube([
            bend_bar_radius * 2,
            bend_bar_radius * 2,
            strip_width + epsilon
        ], center = true);

        // Cutout for resistor
        ry(90)
        cube([
            bend_bar_resistor_cutout_width,
            bend_bar_radius * 2 + epsilon,
            bend_bar_radius * 2 + epsilon
        ], center = true);
    }
}

module lock_bars(punch=false)
{
    ycopies(pixel_cell_spacing, pixel_grid_size)
    lock_bar(punch=punch);
}

module lock_bar(punch=false)
{
    color(lock_bar_assy_color)
    {
        cube([
            lock_bar_width,
            pixel_cell_size,
            (lock_bar_height + epsilon)
        ], anchor = TOP);
        
        tz(-lock_bar_height / 2)
        ycopies(pixel_cell_size, 2)
        xcopies(lock_bar_width - pixel_cell_size, 2)
        sphere(d=lock_sphere_diameter);

        if(punch)
        {
            xcopies(lock_bar_width - lock_bar_height * 2, 2)
            tz(lock_bar_height / 2)
            cube([
                lock_bar_height * 2 + epsilon,
                pixel_cell_size,
                (lock_bar_height + epsilon)
            ], anchor = TOP);

            ycopies(pixel_cell_size, 2)
            xcopies(lock_bar_width - pixel_cell_size, 2)
            tz(-lock_sphere_diameter / 2)
            cyl(h = lock_bar_height * 2 + epsilon, d=lock_sphere_diameter * 0.8, anchor=TOP);

        }
    }

}

strip_seg_length = pixel_cell_size + intra_pixel_spacing;
strip_seg_thickness = 1;

module strips(seg_width = strip_width)
{
    xcopies(pixel_cell_spacing, pixel_grid_size)
    translate([
        -seg_width / 2,
        -pixel_cell_size / 2,
        pixel_cell_depth + strip_seg_thickness / 2
    ])
    ycopies(strip_seg_length, 7)
    strip_segment(seg_width);
}

module strip_segment(seg_width = strip_width)
{
    bent_path = [
        [0, 0], 
        [0 + pixel_cell_size, 0], 
        [0 + pixel_cell_size, bend_bar_height], 
        [0 + pixel_cell_size + bend_bar_width, bend_bar_height], 
        [0 + pixel_cell_size + bend_bar_width, 0],
    ];

    path = [
        [0, bend_bar_height],
        [1, 0], 
        [1 + pixel_cell_size, 0],
        [1 + pixel_cell_size + 1, bend_bar_height], 
        [1 + pixel_cell_size + 1 + bend_bar_width, bend_bar_height], 
    ];

    color("red")
    rx(90)
    ry(90)
    linear_extrude(height=seg_width)
    stroke(path, width=strip_seg_thickness);
}