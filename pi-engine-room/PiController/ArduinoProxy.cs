using System;
using System.Buffers.Binary;
using System.Collections.Generic;
using System.Device.I2c;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace PiController
{
    class ArduinoProxy : IDisposable
    {
        public const byte I2CAddressBase = 0x40;
        public const byte I2CAddressMax = 0x7F;

        private I2cConnectionSettings I2CSettings;
        private I2cDevice I2CDevice;

        public int I2CBusId => I2CSettings.BusId;
        public int ArduinoAddress => I2CSettings.DeviceAddress;

        public ArduinoProxy(int i2cBusId, int arduinoAddress)
        {
            if(arduinoAddress < I2CAddressBase)
            {
                throw new ArgumentOutOfRangeException(nameof(arduinoAddress), $"the I2C address of the Arduino ({arduinoAddress:X}) must be on the range of [{I2CAddressBase:X}, {I2CAddressMax:X}]");
            }
            I2CSettings = new(i2cBusId, arduinoAddress);
            I2CDevice = I2cDevice.Create(I2CSettings);

            Logger.Info($"ArduinoProxy: Creating proxy on I2C Bus: {I2CBusId} and address {ArduinoAddress}");
        }

        /// <inheritdoc/>
        public void Dispose()
        {
            I2CDevice?.Dispose();
            I2CDevice = null!;
        }

        public void SendPing(byte pingValue)
        {
            Logger.Info($"ArduinoProxy: Ping: {pingValue}");
            WriteByte(pingValue);
        }

        private byte ReadByte()
        {
            return I2CDevice.ReadByte();
        }

        private ushort ReadUInt16()
        {
            Span<byte> bytes = stackalloc byte[2];
            I2CDevice.Read(bytes);
            return BinaryPrimitives.ReadUInt16LittleEndian(bytes);
        }

        private void WriteByte(byte data)
        {
            Span<byte> bytes = stackalloc byte[1];
            bytes[0] = data;
            I2CDevice.Write(bytes);
        }

        private void WriteUInt16(ushort value)
        {
            Span<byte> bytes = stackalloc byte[2];
            BinaryPrimitives.WriteUInt16LittleEndian(bytes, value);
            I2CDevice.Write(bytes);
        }
    }
}
