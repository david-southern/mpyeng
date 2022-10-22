// cSpell: ignore centur

export class Utils {
    public static ClampDegrees(angle: number): number {
        let retval = angle % 360;
        if (retval < 0) {
            retval += 360;
        }
        return retval;
    }

    public static Clamp(value: number, min: number, max: number): number {
        return Math.min(Math.max(value, min), max);
    }

    public static DegreesToRadians(degrees: number) {
        return (degrees / 180) * Math.PI;
    }

    public static RadiansToDegrees(radians: number) {
        return (radians / Math.PI) * 180;
    }

    public static SafeGetElement(elementId: string): HTMLElement {
        const checkElement = document.getElementById(elementId);

        if (!checkElement) {
            throw new Error(`SSG element Id '${elementId}' did not select any DOM element`);
        }

        return checkElement;
    }

    /**
     * Returns the totalSeconds as a string in the form of `3.438 days` where the units are the largest unit (up to
     * centuries) that results in a value greater than one.
     * @param totalSeconds 
     * @returns 
     */
    public static HumanTime(totalSeconds: number): string {
        class ScaleFactor {
            public factor: number = null!;
            public unit: string = null!;
            public singularSuffix?: string;
            public pluralSuffix?: string;
        }

        // Yes, I know about Humanizr, but they don't have this format...
        const scaleFactors: ScaleFactor[] = [
            { factor: 60, unit: "minute" },
            { factor: 60, unit: "hour" },
            { factor: 24, unit: "day" },
            { factor: 365, unit: "year" },
            { factor: 10, unit: "decade" },
            { factor: 10, unit: "centur", singularSuffix: "y", pluralSuffix: "ies" }
        ];

        const sign = totalSeconds < 0 ? "-" : "";
        let retTime = Math.abs(totalSeconds);
        let retUnit = "second";
        let singularSuffix = "";
        let pluralSuffix = "s";

        const checkScale = (scale: ScaleFactor): boolean => {
            if (retTime > scale.factor) {
                retTime /= scale.factor;
                retUnit = scale.unit;
                singularSuffix = scale.singularSuffix ?? singularSuffix;
                pluralSuffix = scale.pluralSuffix ?? pluralSuffix;
                return true;
            }
            return false;
        };

        for (const nextFactor of scaleFactors) {
            if (!checkScale(nextFactor)) {
                break;
            }
        }

        return `${sign}${retTime.toFixed(3)} ${retUnit}${(Utils.FloatEQ(retTime, 1, 0.0005)) ? singularSuffix : pluralSuffix}`;
    }

    public static DownloadFromFileInput(fileName: string, htmlFileInput: File) {
        Utils.DownloadFileFromBlob(fileName, htmlFileInput);
    }

    public static DownloadFileFromBlob(fileName: string, blob: Blob) {
        const url = URL.createObjectURL(blob);
        const anchorElement = document.createElement("a");
        anchorElement.href = url;
        anchorElement.download = fileName;
        anchorElement.click();
        anchorElement.remove();
        URL.revokeObjectURL(url);
    }

    /**
     * Tests if value1 and value2 are exactly the same float value, or if either is Infinite or Nan, then if they are
     * both the same Infinite or Nan value.
     */
    private static SimpleFloatEQ(value1: number, value2: number): boolean {
        if (typeof value1 !== "number" || typeof value2 !== "number") {
            return false;
        }

        if (!Number.isFinite(value1) || !Number.isFinite(value2)) {
            return value1 === value2;
        }

        return false;
    }

    /**
     * Return an appropriate divisor for the FloatXX methods.  The divisor will always be positive.
     */
    public static FloatEQDivisor(value1: number, value2: number): number {
        // Handle zero to avoid division by zero
        let divisor = Math.max(value1, value2);
        if (divisor === 0) {
            divisor = Math.min(value1, value2);
        }

        return divisor < 0 ? -divisor : divisor;
    }

    // From the .Net Single docs: https://learn.microsoft.com/en-us/dotnet/api/system.single?view=net-6.0
    // Single.Epsilon is sometimes used as an absolute measure of the distance between two Single values when
    // testing for equality. However, Single.Epsilon measures the smallest possible value that can be added to, or
    // subtracted from, a Single whose value is zero. For most positive and negative Single values, the value of
    // Single.Epsilon is too small to be detected. Therefore, except for values that are zero, we do not recommend
    // its use in tests for equality.
    public static FloatingPointEqualityEpsilon = Number.EPSILON * 100;

    public static FloatEQ(value1: number, value2: number, epsilon = Utils.FloatingPointEqualityEpsilon): boolean {
        if (Utils.SimpleFloatEQ(value1, value2)) {
            return true;
        }

        const divisor = Utils.FloatEQDivisor(value1, value2);

        return Math.abs(value1 - value2) / divisor <= epsilon;
    }

    public static FloatNE(value1: number, value2: number, epsilon = Utils.FloatingPointEqualityEpsilon): boolean {
        return !Utils.FloatEQ(value1, value2, epsilon);
    }

    public static FloatLT(value1: number, value2: number, epsilon = Utils.FloatingPointEqualityEpsilon): boolean {
        if (Utils.SimpleFloatEQ(value1, value2)) {
            return false;
        }

        const divisor = Utils.FloatEQDivisor(value1, value2);

        return (value1 - value2) / divisor < -epsilon;
    }

    public static FloatGT(value1: number, value2: number, epsilon = Utils.FloatingPointEqualityEpsilon): boolean {
        if (Utils.SimpleFloatEQ(value1, value2)) {
            return false;
        }

        const divisor = Utils.FloatEQDivisor(value1, value2);


        return (value1 - value2) / divisor > epsilon;
    }


    public static FloatLE(value1: number, value2: number, epsilon = Utils.FloatingPointEqualityEpsilon): boolean {
        return Utils.SimpleFloatEQ(value1, value2) || Utils.FloatLT(value1, value2, -epsilon);
    }

    public static FloatGE(value1: number, value2: number, epsilon = Utils.FloatingPointEqualityEpsilon): boolean {
        return Utils.SimpleFloatEQ(value1, value2) || Utils.FloatGT(value1, value2, -epsilon);
    }
}
