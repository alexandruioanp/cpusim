def exp(x, n)
(
    if(n = 0) then return 1;
    else return x * exp(x, n-1);
);

write('Recursive: x raised to the nth.');
write(exp(x, n));
writeln; writeln;
