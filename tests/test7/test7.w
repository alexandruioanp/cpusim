{COMS22201 test7: program to test all language features.}
{Already tested: write statements, constants, variables, assignment, read statements, if statements, while loops, arithmetic expressions, boolean expressions.}

x := 12;
write('Factorial of '); write(x); write(' is ');
y := 1;
while !(x=1) do (
  y := y * x;
  x := x - 1
);
write(y);
writeln;
writeln;

write('Exponential calculator'); writeln;
base := 99;
if 1 <= base then (
  write('Enter exponent: ');
  exponent := 5;
  num := 1;
  count := exponent;
  while 1 <= count do (
    num := num * base;
    count := count - 1
  );
  write(base); write(' raised to the power of '); write(exponent); write(' is ');
  write(num)
) else (
  write('Invalid base '); write(base)
);
writeln
