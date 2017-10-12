{COMS22201 test4: program to test if statements.}
{Already tested: write statements and constants.}

if (1 <= 2)
  then write(1)
  else skip;

if 2 = 3
  then write(2)
  else skip;
if 4 = 4
  then ( write(3); writeln )
  else ( write(4); writeln );
if 5 <= 5
  then ( write(5); writeln; writeln )
  else ( write(6); writeln; writeln );
if 6 <= 7
  then write(7)
  else skip;
if 9 <= 8
  then skip
  else write(8);
if 1 <= 2
  then skip
  else write(9);
if 2 = 3
  then write('a')
  else
  ( if 4 = 4
    then write('b')
    else skip
  );
if 5 <= 6
  then
  ( if 7 <= 8
      then write('c')
      else skip;
    if 10 <= 9
      then write('d')
      else write('e')
  )
  else skip
