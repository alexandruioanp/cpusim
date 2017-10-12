{COMS22201 test0: program to test lexical and syntax analysis.}
{This program is not expected to be runnable!}

read(max);
write(max);
writeln;
num := (331*max-3)*2+max;
i1 := 0-4;
read(i2);
if ! num = max
then (
  limit := num;
  if 0-max <= num
  then
    write(3+max*2)
  else
    skip
)
else (
  while i1 <= 2*i2-1
  do
    if longname*2 <= i1 & ! longname*2 = i1
    then
      max := max*3
    else
      skip;
  longname := max
);
while i1 <= limit & ! i1 = limit
do (
  if i1 = i2
  then
    write('yes')
  else
    skip;
  i1 := i1+1
)
