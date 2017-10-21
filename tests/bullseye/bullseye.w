write('Parameters: size=28, rings=10');
size := 28;
nRings := 10;
writeln;
{x and y range from -size to +size}
y := 0 - size;
while y <= size do (
  x := 0 - size;
  while x <= size do (
    distSq := x*x + y*y;  {distSq is square of distance from centre to (x,y)}
    ring := 0;
    while (2*ring + 1) * (2*ring + 1) * (2*size + 1) * (2*size + 1) <=
          distSq * 4 * (2*nRings - 1) * (2*nRings - 1) do
      ring := ring + 1;
    {ring width = (2*size+1)/(2*nRings-1)}
    {loop exits when distance < (ring+1/2)*width = (2*ring+1)*(2*size+1)/(2*(2*nRings-1))}
    if nRings <= ring then
      write(' ')
    else
      write(ring);
    write(' ');
    x := x + 1
  );
  writeln;
  y := y + 1
)
