function fib(n) {
    if (n <= 1) {
        n;
    } else {
        fib(n - 1) + fib(n - 2);
    }
}

function sum_fib(n) {
    total = 0;
    i = 0;
    while (i <= n) {
        total = total + fib(i);
        i = i + 1;
    }
    total;
}

function main() {
    n = 10;
    s = sum_fib(n);
    s;
}

main();