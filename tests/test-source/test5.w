{COMS22201 test5: program to test while loops.}
{Already tested: write statements and constants.}
{Note: need to use the "-j" option of assmule to prevent infinite loops.}

while 1 <= 2 do write(1);
while 3 = 5 do write(2);
while 4 = 4 do write(3);
while 5 <= 4 do ( write(5); writeln; writeln );
while 6 <= 7 do write(7);
while 9 <= 8 do write(8);
while 3 <= 2 do write('a');
while 4 = 4 do write('b');
while 5 <= 6 do
(
  while 7 <= 8 do write('c');
  while 1 <= 9 do write('d')
)
