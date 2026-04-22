Where loops are in startUp.c:
-----------------------------
In main()
while (1) menu loop that keeps asking for task number until 0 exits.
In runTask1()
for (int i = 1; i <= numProcesses; i++) to read processes.
while (!isEmpty(q1) || !isEmpty(q2) || !isEmpty(q3)) main scheduler loop.
Inside it:
while (!isEmpty(q1))
while (!isEmpty(q2) && isEmpty(q1))
while (!isEmpty(q3) && isEmpty(q1) && isEmpty(q2))
In runTask2()
for (int i = 0; i < 5; i++) queue initialization.
for (int i = 1; i <= numProcesses; i++) to read processes.
while (!allEmpty) main scheduler loop.
Inside it:
for (int prio = 0; prio < 5; prio++)
nested for (int hp = 0; hp < prio; hp++)
while (!isEmpty(queues[prio]))
Useful online references (for you to debug)
C scanf behavior and return values: cppreference scanf
Why malformed scanf input causes issues: GNU libc formatted input
Round Robin / MLFQ scheduling concepts: GeeksforGeeks MLFQ
Infinite loop debugging patterns in C: MIT Debugging C programs
-----------------------------