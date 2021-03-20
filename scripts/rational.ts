type Rational = [bigint, bigint];

export function add([a, b]: Rational, [c, d]: Rational): Rational {
    return [a * d + c * b, b * d];
}

export function sub([a, b]: Rational, [c, d]: Rational): Rational {
    return [a * d - c * b, b * d];
}

export function mul([a, b]: Rational, [c, d]: Rational): Rational {
    return [a * c, b * d];
}

export function div(x: Rational, [c, d]: Rational): Rational {
    return mul(x, [d, c]);
}

export function gcd(a: bigint, b: bigint): bigint {
    if (a < b)
        [a, b] = [b, a];
    while (b > 0n)
        [a, b] = [b, a % b];
    return a;
}

export function reduce([a, b]: Rational): Rational {
    const x = gcd(a, b);
    return [a / x, b / x];
}

export function toDecimal([a, b]: Rational, precision: number): string {
    const int = a / b;
    let rem = (a % b) * 10n;
    let digits = [];

    for (let i = 0; rem !== 0n && i <= precision; i++) {
        if (rem < b) {
            rem *= 10n;
            digits.push(0);
        } else {
            digits.push(rem / b);
            rem = (rem % b) * 10n;
        }
    }
    // Round if precision limit was reached
    if (digits.length == precision + 1) {
        digits[digits.length - 1];
    }

    return int.toString();
}
