alloc a[20];

n := 10;
write('Unsorted array: ');
for(i := 1; i <= n; i++)
(
    write(a[i]);
    if(!(i = n)) then write(', ');
    else skip;
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
    if(!(i = n)) then write(', ');
    else skip;
);
writeln;
