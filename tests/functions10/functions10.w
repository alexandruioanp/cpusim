def sum1to(n)
(
    if(n = 0) then return 0;
    else return n + sum1to(n-1);
);

def exp(x, n)
(
    if(n = 0) then return 1;
    else return x * exp(x, n-1);
);

def fact(n)
(
    if(n = 1) then return 1;
    else return n * fact(n-1);
);

def parity(x)
(
    if(x = 2 * (x/2)) then return 0;
    else return 1;
);

alloc a[20];

def part(p, r)
(
    x := a[r];
    h := p - 1;

    for(j := p;  j <= r - 1; j := j + 1)
    (
        if(a[j] <= x) then
        (
            h := h + 1;
            tmp := a[h];
            a[h] := a[j];
            a[j] := tmp;
        );
    );

    tmp := a[h + 1];
    a[h + 1] := a[r];
    a[r] := tmp;

    return h + 1;
);

def qsort(p, r)
(
    if(p < r) then
    (
        q := part(p, r);
        qsort(p, q - 1);
        qsort(q + 1, r);
    );
);

def sc0peDem()
(
    {local variable with the same name as global function}
    qsort := 2;
);

write('Recursive: sum 1 to n. Enter n: ');
{read(n);}
n := 20;
write(sum1to(n));
writeln; writeln;

write('Recursive: x raised to the nth. Enter x: ');
{read(x);}
x := 16;
write('Enter n: ');
{read(n);}
n := 7;
write(exp(x, n));
writeln; writeln;

write('is x odd (1) or even (0)? Enter x : ');
{read(x);}
x := 1001;
write(parity(x));
x := 543126;
write(parity(x));
writeln; writeln;

write('This also demonstrates arrays'); writeln;
write('quicksort. Enter n: ');
{read(n);}
n := 10;
write('Enter '); write(n); write(' numbers: '); writeln;
{for(i := 1; i <= n; i := i + 1)
    read(a[i]);
}
write('Unsorted array: ');
for(i := 1; i <= n; i := i + 1)
(
    write(a[i]);
    if(!(i = n)) then write(', ');
);
writeln;

qsort(1, n);
write('Sorted array: ');
for(i := 1; i <= n; i := i + 1)
(
    write(a[i]);
    if(!(i = n)) then write(', ');
);
writeln;

