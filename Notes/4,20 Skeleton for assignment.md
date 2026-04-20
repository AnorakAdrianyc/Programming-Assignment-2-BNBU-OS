# Programming Assignment Two

Write a program to implement CPU scheduling with Multilevel Feedback Queue.
Please refer to slides 28-29 of Lecture 5 `ch5_CPU_Scheduling.pdf` for Multilevel Feedback Queue and its example.

At the beginning of all `.c` and `.h` files, put a comment including:
- author
- student id
- date
- file purpose

## Task 1

Write a program that includes three queues: `Q1`, `Q2`, and `Q3`.

### Rules

- [ ] `Q1` and `Q2` both use FCFS + RR.
- [ ] `Q3` uses FCFS.
- [ ] `Q1` quantum is `4`; `Q2` quantum is `8`.
- [ ] Each process goes to `Q1` first.
- [ ] If a process is not finished in one quantum in `Q1`, move it to `Q2`.
- [ ] If a process is not finished in one quantum in `Q2`, move it to `Q3`, where it is finished according to FCFS.
- [ ] Processes in `Q1` have highest priority while in `Q3` have lowest priority.
- [ ] Ask the user to enter burst times in arrival order (assume all arrive at time 0 in sequence `P1, P2, P3, …, Pn`).
- [ ] Output the processes in the sequence they use CPU.

### Examples

#### Example 1

```text
================================================
Enter the number of processes to schedule: 3
Enter the burst time of P1: 17
Enter the burst time of P2: 15
Enter the burst time of P3: 7
The scheduling sequence is: P1, P2, P3, P1, P2, P3, P1, P2
================================================
```

#### Example 2

```text
================================================
Enter the number of processes to schedule: 2
Enter the burst time of P1: 3
Enter the burst time of P2: 10
The scheduling sequence is: P1, P2, P2
================================================
```

## Task 2

Task 2 is like Task 1, using Multilevel feedback queue for CPU scheduling with more rules.

### Rules

- [ ] There are 5 priority levels, from `1` to `5`, where `1` is the highest and `5` is the lowest.
- [ ] User inputs burst time and priority for each process.
- [ ] There are at most 5 queues (`Q1` to `Q5`), and each queue contains processes with the corresponding priority.
- [ ] Priority 5 queue uses FCFS; other queues use FCFS + RR.
- [ ] User inputs RR quantum.
- [ ] If a process cannot finish during the given quantum, increase its priority number by 1 (maximum `5`) and move it to the end of the corresponding queue.
- [ ] Assume all processes arrive at time 0.

### Example

```text
================================================
Enter the quantum for Q1, Q2, Q3, and Q4: 6 4 8 7
Enter the number of processes to schedule: 3
Enter the burst time and priority of P1: 24, 1
Enter the burst time and priority of P2: 10, 5
Enter the burst time and priority of P3: 17, 3
The scheduling sequence is: P1, P1, P3, P1, P3, P1, P2, P3
================================================
```

## Submission

- [ ] Given a startup program, merge `main` functions of task1 and task2 into one, so users can test both tasks in one program.

### Example

```text
================================================
Enter a task number (1 or 2) or 0 to exit: 3
Please enter 0, 1 or 2.
Enter a task number (1 or 2) or 0 to exit: 2
Enter the quantum for Q1, Q2, Q3, and Q4: 6 4 8 7
Enter the number of processes to schedule: 3
Enter the burst time and priority of P1: 24,1
Enter the burst time and priority of P2: 10,5
Enter the burst time and priority of P3: 17,3
The scheduling sequence is: P1, P1, P3, P1, P3, P1, P2, P3
Enter a task number (1 or 2) or 0 to exit: 1
Enter the number of processes to schedule: 2
Enter the burst time of P1: 3
Enter the burst time of P2: 10
The scheduling sequence is: P1, P2, P2
Enter a task number (1 or 2) or 0 to exit: 1
Enter the number of processes to schedule: 3
Enter the burst time of P1: 17
Enter the burst time of P2: 15
Enter the burst time of P3: 7
The scheduling sequence is: P1, P2, P3, P1, P2, P3, P1, P2
Enter a task number (1 or 2) or 0 to exit: 0
Press any key to continue...
================================================
```

- [ ] Submit only `.c` and `.h` files into iSpace before the deadline.

## Queue skeleton (corrected, valid C)

```c
#include <stdbool.h>
#include <stdlib.h>

typedef struct Process {
    int pid;
    int burst_time;
    int remaining_time;
    int priority;           // Optional for Task 1, used by Task 2.
    struct Process *next;
} Process;

typedef struct Queue {
    Process *front;
    Process *rear;
} Queue;

// Old snippet issues fixed here:
// - `Typedef`, `Int`, `Void`, `Struct`, `If`, `Return` must be lowercase C keywords.
// - Missing semicolon after `typedef struct Queue ... } Queue;`.
// - `new_p->pid;` did nothing; must assign: `new_p->pid = pid;`.
// - Mixed names (`q` vs `n`) caused undeclared-variable errors.
// - `depqueue` returned `temp` while variable was `tmp`.
// - `isMEpty (Quene*n0{` had typoed function/type names and a missing `)`.
// - No malloc failure checks existed.
Queue *initQueue(void) {
    Queue *q = (Queue *)malloc(sizeof(Queue));
    if (q == NULL) {
        return NULL;
    }

    q->front = NULL;
    q->rear = NULL;
    return q;
}

bool isEmpty(const Queue *q) {
    // Treat NULL queue as empty to avoid crashes in caller checks.
    return (q == NULL || q->front == NULL);
}

bool enqueue(Queue *q, int pid, int burst_time, int remaining_time, int priority) {
    if (q == NULL) {
        return false;
    }

    Process *new_p = (Process *)malloc(sizeof(Process));
    if (new_p == NULL) {
        return false;
    }

    new_p->pid = pid;
    new_p->burst_time = burst_time;
    new_p->remaining_time = remaining_time;
    new_p->priority = priority;
    new_p->next = NULL;

    if (q->rear == NULL) {
        // Empty queue: new node is both front and rear.
        q->front = new_p;
        q->rear = new_p;
        return true;
    }

    q->rear->next = new_p;
    q->rear = new_p;
    return true;
}

// Ownership note:
// dequeue returns the removed node, and the caller must free() it (or re-enqueue it first).
Process *dequeue(Queue *q) {
    if (isEmpty(q)) {
        return NULL;
    }

    Process *out = q->front;
    q->front = q->front->next;

    if (q->front == NULL) {
        // Queue became empty after pop.
        q->rear = NULL;
    }

    out->next = NULL;
    return out;
}

void freeQueue(Queue *q) {
    if (q == NULL) {
        return;
    }

    Process *p;
    while ((p = dequeue(q)) != NULL) {
        free(p);
    }

    free(q);
}
```

## Implementation notes / common pitfalls

- The scheduling sequence means one entry per CPU dispatch/slice (not one entry per time unit).
- In Task 1, `Q3` is FCFS to completion.
- In Task 2, if priority is increased beyond `5`, clamp it to `5` (stay in `Q5`).
