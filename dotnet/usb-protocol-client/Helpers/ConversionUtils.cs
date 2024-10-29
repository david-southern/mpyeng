
using System.Data;

namespace Helpers;

public static partial class Utils
{
    public static string? SafeString(object? thingy, string? defaultValue = null)
    {
        if (thingy == null || thingy == DBNull.Value) return defaultValue;
        if (thingy is string) return thingy as string;
        return $"{thingy}";
    }

    public static int? SafeInt(object? thingy, int? defaultValue = null)
    {
        if (thingy == null || thingy == DBNull.Value) return defaultValue;

        try
        {
            if (thingy is string stringThing && int.TryParse(stringThing, out int retval)) return retval;
            if (thingy is char charThing) return charThing;
            if (thingy is byte byteThing) return byteThing;
            if (thingy is sbyte sbyteThing) return sbyteThing;
            if (thingy is short shortThing) return shortThing;
            if (thingy is ushort ushortThing) return ushortThing;
            if (thingy is int intThing) return intThing;
            if (thingy is uint uintThing) return (int)uintThing;
            if (thingy is long longThing) return (int)longThing;
            if (thingy is ulong ulongThing) return (int)ulongThing;
            if (thingy is decimal decimalThing) return (int)decimalThing;
            if (thingy is float floatThing) return (int)floatThing;
            if (thingy is double doubleThing) return (int)doubleThing;
            if (thingy is bool boolThing) return boolThing ? 1 : 0;
            return Convert.ToInt32(thingy);
        }
        catch (Exception) { }

        return defaultValue;
    }

    public static long? SafeLong(object? thingy, long? defaultValue = null)
    {
        if (thingy == null || thingy == DBNull.Value) return defaultValue;

        try
        {
            if (thingy is string stringThing && long.TryParse(stringThing, out long retval)) return retval;
            if (thingy is char charThing) return charThing;
            if (thingy is byte byteThing) return byteThing;
            if (thingy is sbyte sbyteThing) return sbyteThing;
            if (thingy is short shortThing) return shortThing;
            if (thingy is ushort ushortThing) return ushortThing;
            if (thingy is int intThing) return intThing;
            if (thingy is uint uintThing) return uintThing;
            if (thingy is long longThing) return longThing;
            if (thingy is ulong ulongThing) return (long)ulongThing;
            if (thingy is decimal decimalThing) return (long)decimalThing;
            if (thingy is float floatThing) return (long)floatThing;
            if (thingy is double doubleThing) return (long)doubleThing;
            if (thingy is bool boolThing) return boolThing ? 1 : 0;
            return Convert.ToInt64(thingy);
        }
        catch (Exception) { }

        return defaultValue;
    }

    public static ulong? SafeULong(object? thingy, ulong? defaultValue = null)
    {
        if (thingy == null || thingy == DBNull.Value) return defaultValue;

        try
        {
            if (thingy is string stringThing && ulong.TryParse(stringThing, out ulong retval)) return retval;
            if (thingy is char charThing) return charThing;
            if (thingy is byte byteThing) return byteThing;
            if (thingy is sbyte sbyteThing) return (ulong)sbyteThing;
            if (thingy is short shortThing) return (ulong)shortThing;
            if (thingy is ushort ushortThing) return ushortThing;
            if (thingy is int intThing) return (ulong)intThing;
            if (thingy is uint uintThing) return uintThing;
            if (thingy is long longThing) return (ulong)longThing;
            if (thingy is ulong ulongThing) return ulongThing;
            if (thingy is decimal decimalThing) return (ulong)decimalThing;
            if (thingy is float floatThing) return (ulong)floatThing;
            if (thingy is double doubleThing) return (ulong)doubleThing;
            if (thingy is bool boolThing) return (ulong)(boolThing ? 1 : 0);
            return Convert.ToUInt64(thingy);
        }
        catch (Exception) { }

        return defaultValue;
    }

    public static double? SafeDouble(object? thingy, double? defaultValue = null)
    {
        if (thingy == null || thingy == DBNull.Value) return defaultValue;

        try
        {
            if (thingy is string stringThing && double.TryParse(stringThing, out double retval)) return retval;
            if (thingy is char charThing) return charThing;
            if (thingy is byte byteThing) return byteThing;
            if (thingy is sbyte sbyteThing) return sbyteThing;
            if (thingy is short shortThing) return shortThing;
            if (thingy is ushort ushortThing) return ushortThing;
            if (thingy is int intThing) return intThing;
            if (thingy is uint uintThing) return uintThing;
            if (thingy is long longThing) return longThing;
            if (thingy is ulong ulongThing) return ulongThing;
            if (thingy is decimal decimalThing) return (double)decimalThing;
            if (thingy is float floatThing) return floatThing;
            if (thingy is double doubleThing) return doubleThing;
            if (thingy is bool boolThing) return boolThing ? 1 : 0;
            return Convert.ToDouble(thingy);
        }
        catch (Exception) { }

        return defaultValue;
    }

    public static decimal? SafeDecimal(object? thingy, decimal? defaultValue = null)
    {
        if (thingy == null || thingy == DBNull.Value) return defaultValue;

        try
        {
            if (thingy is string stringThing && decimal.TryParse(stringThing, out decimal retval)) return retval;
            if (thingy is char charThing) return charThing;
            if (thingy is byte byteThing) return byteThing;
            if (thingy is sbyte sbyteThing) return sbyteThing;
            if (thingy is short shortThing) return shortThing;
            if (thingy is ushort ushortThing) return ushortThing;
            if (thingy is int intThing) return intThing;
            if (thingy is uint uintThing) return uintThing;
            if (thingy is long longThing) return longThing;
            if (thingy is ulong ulongThing) return ulongThing;
            if (thingy is decimal decimalThing) return decimalThing;
            if (thingy is float floatThing) return (decimal)floatThing;
            if (thingy is double doubleThing) return (decimal)doubleThing;
            if (thingy is bool boolThing) return boolThing ? 1 : 0;
            return Convert.ToDecimal(thingy);
        }
        catch (Exception) { }

        return defaultValue;
    }

    public static DateTime? SafeDateTime(object? thingy, DateTime? defaultValue = null)
    {
        if (thingy == null || thingy == DBNull.Value) return defaultValue;

        try
        {
            if (thingy is string stringThing && DateTime.TryParse(stringThing, out DateTime retval)) return retval;
            return Convert.ToDateTime(thingy);
        }
        catch (Exception) { }

        return defaultValue ?? DateTime.MinValue;
    }

    public static bool? SafeBoolean(object? thingy, bool? defaultValue = null)
    {
        if (thingy == null || thingy == DBNull.Value) return defaultValue;

        try
        {
            if (thingy is string stringThing)
            {
                if (bool.TryParse(stringThing, out bool retval)) return retval;
                stringThing = stringThing.ToLower();
                return stringThing == "1"
                    || stringThing == "t" || stringThing == "true"
                    || stringThing == "y" || stringThing == "yes";
            }
            if (thingy is char charThing) return charThing != 0;
            if (thingy is byte byteThing) return byteThing != 0;
            if (thingy is sbyte sbyteThing) return sbyteThing != 0;
            if (thingy is short shortThing) return shortThing != 0;
            if (thingy is ushort ushortThing) return ushortThing != 0;
            if (thingy is int intThing) return intThing != 0;
            if (thingy is uint uintThing) return uintThing != 0;
            if (thingy is long longThing) return longThing != 0;
            if (thingy is ulong ulongThing) return ulongThing != 0;
            if (thingy is decimal decimalThing) return decimalThing != 0;
            if (thingy is float floatThing) return floatThing != 0;
            if (thingy is double doubleThing) return doubleThing != 0;
            if (thingy is bool boolThing) return boolThing;
            return Convert.ToBoolean(thingy);
        }
        catch (Exception) { }

        return defaultValue;
    }

    public static Dictionary<string, object?> AsDictionary(this DataRow? row)
    {
        Dictionary<string, object?> retval = new Dictionary<string, object?>();

        if (row?.Table?.Columns?.Count > 0)
        {
            for (int colIndex = 0; colIndex < row.Table.Columns.Count; colIndex++)
            {
                object? colValue = row.ItemArray?.Length > colIndex ? row.ItemArray[colIndex] : "<unset>";
                retval[row.Table.Columns[colIndex].ColumnName] = colValue;
            }
        }

        return retval;
    }

    public static string? SafeString(this DataRow? row, string colName)
    {
        object? rowVal = row?[colName] ?? null;
        return SafeString(rowVal);
    }

    public static int? SafeInt(this DataRow row, string colName)
    {
        object? rowVal = row?[colName] ?? null;
        return SafeInt(rowVal);
    }

    public static DateTime? SafeDateTime(this DataRow? row, string colName)
    {
        object? rowVal = row?[colName] ?? null;
        return SafeDateTime(rowVal);
    }

    public static decimal? SafeDecimal(this DataRow? row, string colName)
    {
        object? rowVal = row?[colName] ?? null;
        return SafeDecimal(rowVal);
    }

    public static decimal? SafeRound(this decimal? thingy, int decimals = 0)
    {
        if (thingy == null) { return thingy; }
        return thingy.Value.SafeRound(decimals);
    }

    public static decimal SafeRound(this decimal thingy, int decimals = 0)
    {
        return Math.Round(thingy, decimals);
    }

    public static double? SafeRound(this double? thingy, int decimals = 0)
    {
        if (thingy == null) { return thingy; }
        return thingy.Value.SafeRound(decimals);
    }

    public static double SafeRound(this double thingy, int decimals = 0)
    {
        return Math.Round(thingy, decimals);
    }

    /// <summary>
    /// Performs a deep clone of the source object by serializing to and from JSON.
    /// </summary>
    public static T? CloneDeep<T>(this T? source)
    {
        // Don't serialize a null object, simply return the default for that object
        if (source == null)
        {
            return default;
        }

        var serializeSettings = new JsonSerializerSettings
        {
            ReferenceLoopHandling = ReferenceLoopHandling.Ignore
        };

        string cloneJSON = JsonConvert.SerializeObject(source, serializeSettings);

        var deserializeSettings = new JsonSerializerSettings
        {
            ObjectCreationHandling = ObjectCreationHandling.Replace
        };

        return JsonConvert.DeserializeObject<T>(cloneJSON, deserializeSettings);
    }

    public static string? SafeJson(this object? thingy, bool formatted = false)
    {
        return JsonConvert.SerializeObject(thingy, formatted ? Formatting.Indented : Formatting.None,
            new JsonSerializerSettings { ReferenceLoopHandling = ReferenceLoopHandling.Ignore });
    }

    public static string FormatI2CPort(int port)
    {
        if (port < 1 || port > 0x77) { return "I2C Error: Invalid Port: {port}"; }

        return $"0x{port:X2}";
    }

    public static string FormatI2CPortList(List<int> portList)
    {
        return string.Join(", ", portList.Select(p => FormatI2CPort(p)));
    }
}
