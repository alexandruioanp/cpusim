alloc a[101];

{write('insertion sort. Enter n: ');
read(n);
write('Enter '); write(n); write(' numbers: '); writeln;
for(i := 1; i <= n; i++)
    read(a[i]);
}
n := 100;
write('Unsorted array: ');
for(i := 1; i <= n; i++)
(
    write(a[i]);
    writeln;
);
writeln;

for(j := 2; j <= n; j++)
(
    key := a[j];
    i := j - 1;
    while(i > 0 & a[i] > key) do
    (
        a[i + 1] := a[i];
        i := i - 1;
    );
    a[i + 1] := key;
);

write('Sorted array: ');
for(i := 1; i <= n; i++)
(
    write(a[i]);
    writeln;
);
writeln;
