include <BOSL/constants.scad>
use <BOSL/shapes.scad>
use <BOSL/transforms.scad>
use <lazy.scad>
use <rounded_collar.scad>

$fn = 67;

// Render/view settings
laser_cut = false;

cutaway_view = false;
show_card = false;
show_photo_slots = false;
show_lighting = false;
show_support_board = false;

// Printer settings
difference_fudge = 0.01;
extrusion_fudge = 0.1;
print_layer_height = 0.15;

// Default minimum thickness of any wall
wall_thickness = 2;

// Thickness of the engineering board support plate.
support_board_thickness = (3 / 16) * 25.4;

// Thickness of the card acrylic
// acrylic_thickness = 3.25;
acrylic_thickness = 6.2;

// Card dimensions
card_width = 54;
card_height = 81;
card_thickness = 6.2; // Allow thickness to be variable in case we add any 'decorations' around the card
card_corner_fillet = 2;

// Lighting dimensions
LED_strip_width = 12;
LED_strip_height = 1;
LED_width = 5.2;
LED_height = 2;
// What is the minimum length at which that the physical strip may be cut?
LED_unit_length = 7;
// How much space at each end of the strip do I need to solder the LED wiring?
LED_wiring_allowance = 4;

// If true, the LED strip module will include an acrylic plate to protect the exposed LEDs
lighting_includes_acrylic = false;
lighting_height = LED_strip_height + LED_height + (lighting_includes_acrylic ? acrylic_thickness : 0);

// The card slot should be just a bit wider than the cards so that the user can slide it in and out of the slot easily
// and quickly.  The card_support_play indicates how much wider than the card the slot should be.
card_support_play = 2;

front_wall_thickness = 3;
side_wall_thickness = 6;

// At the bottom of the card we'll have the slot-photo-interruptors that will detect the card.
photo_slot_count = 5;

photo_slot_width = 6;   // The side-to-side width of the photo interruptor slot
photo_slot_depth = 10;  // The front-to-back depth of the slot - this is the dimension that the card will fall into
photo_slot_height = 12; // The height from the top of the slot arm to the base of the slot - this is the height that the
// card will project into the slot

photo_slot_case_width = 6;   // The side-to-side width of the photo interruptor casing
photo_slot_case_depth = 18;  // The front-to-back depth of the casing
photo_slot_case_height = 15; // The height from the top of the slot arm to the base of the casing

photo_slot_base_height = photo_slot_case_height - photo_slot_height;
photo_slot_arm_depth = (photo_slot_case_depth - photo_slot_depth) / 2;

// This is the bottom-most plate that supports the slot assembly
photo_slot_support_thickness = photo_slot_base_height + front_wall_thickness;

// How far should the casing be pushed into the holder so that it doesn't block the card's drop and stick through the
// board
photo_slot_underlap = 0 * photo_slot_arm_depth;

// This is the y-position of the bottom of the card, resting in the bottom of the slot
card_resting_height = photo_slot_support_thickness + photo_slot_base_height;

// The card holder has an open slot in front so the user can see the card.  The slot has a 'flange' on either side so
// that the card doesn't fall out.  This is the width of each of those flanges.
card_support_horizontal_flange_width = 2;
card_support_vertical_flange_width = photo_slot_case_height - photo_slot_base_height + 1;

// This is the front-to-back play at the bottom of the card slot wedge.
card_wedge_play = 1;

card_wedge_width = card_width + card_support_play;

// This is the depth of the bottom of the card slot wedge.  It determines how much front-to-back play there will be when
// the card sits in the slot.
card_wedge_bottom_depth = max(card_thickness + card_wedge_play, photo_slot_case_depth - photo_slot_arm_depth);

// This is the depth of the top of the card slot wedge.  It determines how 'steep' the slot wedge should be
// - how far forward will the card lean when sitting in the slot.  If the top depth is the same as the bottom depths,
//   the slot will be perfectly straight.
card_wedge_top_depth = card_wedge_bottom_depth + card_thickness;

// Dimensions of the card holder itself
holder_depth = max(card_wedge_top_depth, card_wedge_bottom_depth) + front_wall_thickness;
holder_width = card_width + side_wall_thickness * 2 + lighting_height * 2;

// Making the entire height of the holder the same as the card height will cause the card to poke out of the top of the
// holder by the same amount as the card_resting_height. Adjust the holder height up or down to change the 'poke out'.
holder_height = card_height;
holder_corner_fillet = 3;

// Calculae how much space should there be between each slot

// Don't include the fillet corners in the width, we only want the card tabs on the flat part of the base of the
// card.  Add an extra bit of fudge so that there's plenty of slack for the tab/slot interface
photo_slot_width_fudge = 0;
slot_available_width = card_width - (card_corner_fillet * 2) - photo_slot_width_fudge;
slot_space_remaining = slot_available_width - (photo_slot_count * photo_slot_width);
slot_spacing = slot_space_remaining / (photo_slot_count - 1);

echo("In this model:");
echo(str("    there are ", photo_slot_count, " photo slots"));
echo(str("    the slots are ", photo_slot_width, " mm wide and ", photo_slot_depth, " mm deep"));
echo(str("    the slots are spaced ", slot_spacing, " mm apart"));

LED_strip_length = holder_height - card_resting_height - wall_thickness;
LED_bulb_count = floor((LED_strip_length - LED_wiring_allowance * 2) / LED_unit_length);
cut_strip_length = LED_bulb_count * LED_unit_length;
echo(str("    each LED strip (cut to ", cut_strip_length, " mm) will have ", LED_bulb_count, " LED bulbs (with an ",
         LED_wiring_allowance, " mm wiring allowance)"));

mounting_pin_diam = 3;
mounting_pin_projection = 5;
mounting_pin_depth = support_board_thickness + mounting_pin_projection;

if (laser_cut)
{
    projection(cut = true) tz(holder_depth / 2 - holder_corner_fillet - difference_fudge) rx(90) difference()
    {
        card_holder();
        ty(-holder_depth)
        {
            photo_slots();
            mounting_pins();
            // The strip is aligned to the back of the holder.  For the laser cut, center it again so that the LED bulbs
            // are included in the laser cut
            ty(LED_strip_width / 2) lighting();
        }
    }
}
else
{
    if (cutaway_view)
    {
        cutaway_offset = -5;
        bottom_half(s = max(card_width, card_height) * 3)
            left_half(x = cutaway_offset, s = max(card_width, card_height) * 3)
        {
            // bottom_half(s = max(card_width, card_height) * 3)
            {
                card_holder();
                if (show_card)
                {
                    card();
                }
                if (show_photo_slots)
                {
                    photo_slots();
                }
                if (show_lighting)
                {
                    lighting(false);
                }
                if (show_support_board)
                {
                    color("tan") ty(support_board_thickness / 2)
                        cuboid([ holder_width * 125, holder_height * 1.25, support_board_thickness ]);
                }
            }
        }
    }
    else
    {
        card_holder();
        if (show_card)
        {
            card();
        }
        if (show_photo_slots)
        {
            photo_slots();
        }
        if (show_lighting)
        {
            lighting();
        }
        if (show_support_board)
        {
            color("tan") ty(holder_depth / 2 + support_board_thickness / 2)
                cuboid([ holder_width * 1.25, support_board_thickness, holder_height * 1.25 ]);
        }
    }
}

module card_holder()
{
    difference()
    {
        card_blank();
        tz(difference_fudge) photo_slots();
        if (!laser_cut)
        {
            card_slot();
            card_wedge();
        }

        // ty(difference_fudge) lighting();
    }
    mounting_pins();
}

module card_blank()
{
    cuboid([ holder_width, holder_depth, holder_height ],
           // fillet=holder_corner_fillet,
           chamfer = holder_corner_fillet, edges = EDGES_Y_ALL + EDGES_FRONT);
}

module mounting_pins()
{
    holder_sides_width = holder_width - card_wedge_width - lighting_height * 2;

    ty(mounting_pin_depth / 2 + holder_depth / 2 - difference_fudge) xspread(holder_width - holder_sides_width / 2)
        zspread(holder_height * 0.75) ycyl(d = mounting_pin_diam, h = mounting_pin_depth);
}

module photo_slots()
{
    extra_difference_y = 1;
    extra_difference_z = 5;

    color("red")
        tyz(photo_slot_case_depth / 2     // Align from the front of the casing
                + holder_depth / 2        // line up with the back of the holder
                - card_wedge_bottom_depth // push into the holder the depth of the card wedge bottom
                - photo_slot_arm_depth    // plus one slot arm
                - extra_difference_y      // push further into the holder under the card slot so that the edge of
                                          // the casing does not block the cards
            ,
            -holder_height / 2 + card_resting_height + photo_slot_case_height / 2 // Align to the card resting plane
                - photo_slot_base_height // Push into the base support so that the bottom of the slot aligns with
                                         // the card resting plane
        )
    {
        if (laser_cut)
        {
            hull()
            {
                xspread(photo_slot_case_width + slot_spacing, n = photo_slot_count) difference()
                {
                    cuboid([ photo_slot_case_width, photo_slot_case_depth, photo_slot_case_height ]);
                    tz(photo_slot_base_height / 2 + +difference_fudge) cuboid([
                        photo_slot_case_width + difference_fudge, photo_slot_depth, photo_slot_height + difference_fudge
                    ]);
                }
            }
        }
        else
        {
            xspread(photo_slot_case_width + slot_spacing, n = photo_slot_count) difference()
            {
                union()
                {
                    cuboid([
                        photo_slot_case_width, photo_slot_case_depth + extra_difference_y * 2 + difference_fudge,
                        photo_slot_case_height +
                        extra_difference_z
                    ]);
                    cuboid([
                        photo_slot_case_width - 4, photo_slot_case_depth + extra_difference_y * 2 + difference_fudge,
                        photo_slot_case_height * 2
                    ]);
                }

                if (show_photo_slots)
                {
                    tz(photo_slot_base_height / 2 + difference_fudge) cuboid([
                        photo_slot_case_width + difference_fudge, photo_slot_depth,
                        photo_slot_height + extra_difference_z * 2 +
                        difference_fudge
                    ]);
                }
            }
        }
    }
}

module card_slot()
{
    // This is the cutout to make the card visible, it is inset from the card edges and the card_resting_height by
    // card_support_horizontal_flange_width so the card won't fall out
    tz(card_support_vertical_flange_width + card_resting_height)
        cuboid([ card_width - card_support_horizontal_flange_width * 2, holder_depth * 2, card_height ]);
}

wedge_offset = -holder_depth / 2 + front_wall_thickness * 2 + card_wedge_top_depth / 2;

module card_wedge()
{
    card_cutout_height = (card_height - card_resting_height) + difference_fudge;

    // Card slot cutout - wedge
    tyz(wedge_offset + 0.2, card_resting_height - holder_height / 2) prismoid(
        size1 = [ card_wedge_width, card_wedge_bottom_depth ], size2 = [ card_wedge_width, card_wedge_top_depth ],
        h = card_cutout_height, shift = [ 0, -(card_wedge_top_depth - card_wedge_bottom_depth) / 2 ]);
}

module card()
{
    color("red", 0.25) tyz(holder_depth / 2 - card_thickness / 2, card_resting_height)
        cuboid([ card_width, card_thickness, card_height ], fillet = card_corner_fillet, edges = EDGES_Y_ALL);
}

module lighting(render_punchouts = true)
{
    led_strip_z_offset = LED_strip_length / 2 - holder_height / 2 + card_resting_height;

    // If true, then align the LED strip with the slope of the wedge slot, rather than the back of the holder
    rotate_led_strip = true;

    if (rotate_led_strip)
    {
        delta_wedge = card_wedge_top_depth - card_wedge_bottom_depth;
        // Align the front edge of the LED bulbs with the front edge of the wedge.
        led_depth_offset = card_wedge_bottom_depth - LED_width / 2 + delta_wedge / 2;

        align_angle = atan(delta_wedge / LED_strip_length);
        echo(align_angle = align_angle);

        tyz(wedge_offset - 0 * led_depth_offset, led_strip_z_offset) rx(align_angle) lighting_led_strips(true);

        // Clip off the front 2mm of the strip base so we don't punch through the front of the holder
        intersection()
        {
            tyz(wedge_offset - 0 * led_depth_offset, led_strip_z_offset) rx(align_angle) lighting_led_strips(true);
            ty(2) cuboid([ holder_width, holder_depth, holder_height ]);
        }

        if (render_punchouts)
        {
            rotational_punch_fudge = 0.5;

            // Punch out the sides of the card holder behind the LED strip
            tyz(holder_depth / 2 - card_wedge_bottom_depth / 2 + difference_fudge,
                led_strip_z_offset + rotational_punch_fudge / 2)
            {
                skew_xy(0, -align_angle)
                {
                    tx(-card_wedge_width / 2 - lighting_height / 2 + difference_fudge)
                        cuboid([ lighting_height, card_wedge_bottom_depth, LED_strip_length + rotational_punch_fudge ]);
                    tx(card_wedge_width / 2 + lighting_height / 2 - difference_fudge)
                        cuboid([ lighting_height, card_wedge_bottom_depth, LED_strip_length + rotational_punch_fudge ]);
                }

                tx(-card_wedge_width / 2 - lighting_height / 2 + difference_fudge)
                    cuboid([ lighting_height, card_wedge_bottom_depth, LED_strip_length + rotational_punch_fudge ]);
                tx(card_wedge_width / 2 + lighting_height / 2 - difference_fudge)
                    cuboid([ lighting_height, card_wedge_bottom_depth, LED_strip_length + rotational_punch_fudge ]);
            }
        }
    }
    else
    {
        // Align the center of the LED bulbs with the center of the card, assuming that the card is pressed against the
        // back wall.
        led_depth_offset = max(LED_width / 2, card_wedge_bottom_depth / 2);
        tyz(holder_depth / 2 - led_depth_offset, led_strip_z_offset) lighting_led_strips();

        if (render_punchouts)
        {
            // If the led offset is greater than the led width (i.e. the card is thicker than the LED bulb) then lay in
            // a copy of the strip aligned with the back of the holder, so we don't have a thin strip of "back wall"
            // generated
            if (led_depth_offset > (LED_width / 2))
            {
                tyz(holder_depth / 2, led_strip_z_offset) lighting_led_strips();
            }
        }
    }
}

module lighting_led_strips(include_strip_base = true)
{
    tx(-card_wedge_width / 2 - lighting_height + difference_fudge) ry(90) led_strip(include_strip_base);

    tx(card_wedge_width / 2 + lighting_height - difference_fudge) ry(-90) led_strip(include_strip_base);
}

module led_strip(include_strip_base = true)
{
    if (include_strip_base)
    {
        color("black") upcube([ LED_strip_length, LED_strip_width, LED_strip_height ]);
    }

    color("white") translate([ 0, 0, LED_strip_height ]) upcube([ LED_strip_length, LED_width, LED_height ]);

    if (lighting_includes_acrylic)
    {
        translate([ 0, 0, LED_strip_height + LED_height ]) color("#aaaaaa", 0.3)
            upcube([ LED_strip_length, LED_strip_width, acrylic_thickness ]);
    }
}