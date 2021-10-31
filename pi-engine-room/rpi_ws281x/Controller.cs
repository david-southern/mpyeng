using System.Collections.Generic;
using System.Drawing;
using System.Linq;

namespace rpi_ws281x
{
    /// <summary>
    /// Represents the controller which drives the LEDs
    /// </summary>
    public class Controller
	{
		internal Controller(int ledCount, Pin pin, byte  brightness, bool invert, StripType stripType, ControllerType controllerType)
		{
			IsDirty = false;

			Pin = pin;
			GPIOPin = (int)pin;
			Invert = invert;
			Brightness = brightness;
			StripType = stripType;
			ControllerType = controllerType;

			LEDColors = new Color[ledCount];
			for (var i = 0; i < ledCount; i++) {
				LEDColors[i] = Color.Empty;
			}
		}

		/// <summary>
		/// Set LED to a Color
		/// </summary>
		/// <param name="ledID">LED to set (0 based)</param>
		/// <param name="color">Color to use</param>
		public void SetLED(int ledID, Color color) {
			var cName = StripType.ToString();
			if (cName.Contains("W") && cName.Contains("SK")) {
				color = ColorClamp.ClampAlpha(color);
			}
			LEDColors[ledID] = color;
			IsDirty = true;
		}
		
		public void SetLEDS(Color[] color) {
			LEDColors = color;
			IsDirty = true;
		}

		/// <summary>
		/// Set all the LEDs in the strip to same color
		/// </summary>
		/// <param name="color">color to set all the LEDs</param>
		public void SetAll(Color color) {
			var cName = StripType.ToString();
			if (cName.Contains("W") && cName.Contains("SK")) {
				color = ColorClamp.ClampAlpha(color);
			}

			for (var i = 0; i < LEDColors.Length; i++) {
				LEDColors[i] = color;
			}
			IsDirty = true;
		}
		
		/// <summary>
		/// array of LEDs with numeric color values
		/// </summary>
		/// <param name="clearDirty">reset dirty flag</param>
		internal int[] GetColors(bool clearDirty = false)
		{
			if (clearDirty) IsDirty = false;
			var op = new int[LEDColors.Length];
			for (var i = 0; i < LEDColors.Length; i++) {
				op[i] = LEDColors[i].ToArgb();
			}

			return op;
		}
		
		internal Color[] LEDColors { get; private set; }

		/// <summary>
		/// Returns the GPIO pin which is connected to the LED strip
		/// </summary>
		internal int GPIOPin { get; private set; }

		/// <summary>
		/// Returns the Pin used to connect to the LED strip
		/// </summary>
		public Pin Pin { get; private set; }

		/// <summary>
		/// Returns a value which indicates if the signal needs to be inverted.
		/// Set to true to invert the signal (when using NPN transistor level shift).
		/// </summary>
		public bool Invert { get; private set; }

		/// <summary>
		/// Gets or sets the brightness of the LEDs
		/// 0 = darkes, 255 = brightest
		/// </summary>
		public byte Brightness { get; set; }

		/// <summary>
		/// Returns the type of the channel.
		/// The type defines the ordering of the colors.
		/// </summary>
		public StripType StripType { get; private set; }

        /// <summary>
        /// Returns all LEDs on this channel
        /// </summary>
        public IReadOnlyCollection<Color> LEDs => LEDColors;

		/// <summary>
		/// The number of LEDs in the strip
		/// </summary>
        public int LEDCount {
			get => LEDColors.Length;
			set {
				LEDColors = Enumerable.Range(0, value).Select(x => Color.Empty).ToArray();
				IsDirty = true;
			}
		}

		/// <summary>
		/// The type of controller (i.e. PWM, PCM, SPI  )
		/// </summary>
		/// <value></value>
		public ControllerType ControllerType { get; private set; }

		/// <summary>
		/// Indicates if the colors assigned to the LED has changed and the LED should be updated.
		/// </summary>
		internal bool IsDirty { get; set; }
	}
}
