/****************************************************************************
 *                                                                          *
 * Author		: Lam Yuk Cho Adrian                                      *
 *                                                                          *
 * Student ID	: v530000086                                                *
 *                                                                          *
 * Date			: 4/19                                                      *
 *                                                         					*
 * Purpose		: Programming Assignment 2 - Multilevel Feedback Queue      *
 *                                                          					*
 ****************************************************************************/

#include <stdio.h>
#include <stdlib.h>

typedef struct Process {
    int pid;
    int burst_time;
    int remaining_time;
    struct Process *next;
} Process;

typedef struct Queue {
    Process *front;
    Process *rear;
} Queue;

Queue* initQueue() {
    Queue *q = (Queue*)malloc(sizeof(Queue));
    q->front = q->rear = NULL;
    printf("[DEBUG] initQueue: created queue at %p\n", (void*)q);
    return q;
}

void enterQueue(Queue *q, int pid, int burst, int remaining) {
    Process *new_p = (Process*)malloc(sizeof(Process));
    new_p->pid = pid;
    new_p->burst_time = burst;
    new_p->remaining_time = remaining;
    new_p->next = NULL;
    printf("[DEBUG] enterQueue: q=%p pid=%d burst=%d remaining=%d\n",
           (void*)q, pid, burst, remaining);

    if (q->rear == NULL) {
        q->front = q->rear = new_p;
        return;
    }

    q->rear->next = new_p;
    q->rear = new_p;
}

Process* depQueue(Queue *q) {
    if (q->front == NULL) return NULL;

    Process *temp = q->front;
    q->front = q->front->next;
    if (q->front == NULL) q->rear = NULL;
    printf("[DEBUG] depQueue: q=%p pid=%d remaining=%d\n",
           (void*)q, temp->pid, temp->remaining_time);
    return temp;
}

int isEmpty(Queue *q) {
    return q->front == NULL;
}

void runTask1();
void runTask2();

int main() {
    while (1) {
        printf("\nEnter a task number (1 or 2) or 0 to exit: ");
        int taskNo = 0;
        scanf("%d", &taskNo);
        printf("[DEBUG] main: selected task=%d\n", taskNo);
        switch (taskNo) {
            case 0: exit(0);
            case 1: runTask1(); break;
            case 2: runTask2(); break;
            default: printf("Please enter 0, 1 or 2.\n");
        }
    }
}

void runTask1() {
    int numProcesses;

    printf("Enter the number of processes to schedule: ");
    scanf("%d", &numProcesses);
    printf("[DEBUG] runTask1: numProcesses=%d\n", numProcesses);

    Queue *q1 = initQueue();
    Queue *q2 = initQueue();
    Queue *q3 = initQueue();

    for (int i = 1; i <= numProcesses; i++) {
        int burst;
        printf("Enter the burst time of P%d: ", i);
        scanf("%d", &burst);
        printf("[DEBUG] runTask1: enqueue P%d burst=%d into Q1\n", i, burst);
        enterQueue(q1, i, burst, burst);
    }

    printf("The scheduling sequence is: ");

    int quantum1 = 4;
    int quantum2 = 8;
    int first = 1;

    while (!isEmpty(q1) || !isEmpty(q2) || !isEmpty(q3)) {
        while (!isEmpty(q1)) {
            Process *p = depQueue(q1);

            if (!first) printf(", ");
            printf("P%d", p->pid);
            first = 0;

            if (p->remaining_time <= quantum1) {
                printf("[DEBUG] runTask1: P%d finished in Q1\n", p->pid);
                free(p);
            } else {
                p->remaining_time -= quantum1;
                printf("[DEBUG] runTask1: P%d demoted to Q2 remaining=%d\n",
                       p->pid, p->remaining_time);
                enterQueue(q2, p->pid, p->burst_time, p->remaining_time);
                free(p);
            }
        }

        while (!isEmpty(q2) && isEmpty(q1)) {
            Process *p = depQueue(q2);

            if (!first) printf(", ");
            printf("P%d", p->pid);
            first = 0;

            if (p->remaining_time <= quantum2) {
                printf("[DEBUG] runTask1: P%d finished in Q2\n", p->pid);
                free(p);
            } else {
                p->remaining_time -= quantum2;
                printf("[DEBUG] runTask1: P%d moved to Q3 remaining=%d\n",
                       p->pid, p->remaining_time);
                enterQueue(q3, p->pid, p->burst_time, p->remaining_time);
                free(p);
            }
        }

        while (!isEmpty(q3) && isEmpty(q1) && isEmpty(q2)) {
            Process *p = depQueue(q3);

            if (!first) printf(", ");
            printf("P%d", p->pid);
            first = 0;

            free(p);
        }
    }

    printf("\n");
}
void runTask2() {
    int quantums[4];
    int numProcesses;

    printf("Enter the quantum for Q1, Q2, Q3, and Q4: ");
    scanf("%d %d %d %d", &quantums[0], &quantums[1], &quantums[2], &quantums[3]);
    printf("[DEBUG] runTask2: input quantums=%d,%d,%d,%d\n",
           quantums[0], quantums[1], quantums[2], quantums[3]);
    // Validate quantums to prevent infinite loops / TLE (per assignment robustness)
    for (int i = 0; i < 4; i++) {
        if (quantums[i] <= 0) {
            quantums[i] = 1;  // default to safe positive value as per PDF intent
            printf("[DEBUG] runTask2: corrected quantum[%d] to 1\n", i);
        }
    }

    printf("Enter the number of processes to schedule: ");
    scanf("%d", &numProcesses);
    printf("[DEBUG] runTask2: numProcesses=%d\n", numProcesses);

    Queue *queues[5];
    int priorities[100] = {0};

    for (int i = 0; i < 5; i++) {
        queues[i] = initQueue();
    }

    for (int i = 1; i <= numProcesses; i++) {
        int burst, priority;
        printf("Enter the burst time and priority of P%d: ", i);
        // Fixed formatting per PDF example (accepts "24,1" or "24, 1") and to_fix2.md notes
        scanf(" %d ,%d", &burst, &priority);

        if (priority < 1) priority = 1;
        if (priority > 5) priority = 5;
        printf("[DEBUG] runTask2: enqueue P%d burst=%d priority=%d\n",
               i, burst, priority);

        priorities[i] = priority;
        enterQueue(queues[priority - 1], i, burst, burst);
    }

    printf("The scheduling sequence is: ");

    int first = 1;
    int allEmpty = 0;

    while (!allEmpty) {
        allEmpty = 1;

        for (int prio = 0; prio < 5; prio++) {
            int higherHasProcesses = 0;
            for (int hp = 0; hp < prio; hp++) {
                if (!isEmpty(queues[hp])) {
                    higherHasProcesses = 1;
                    break;
                }
            }

            if (higherHasProcesses) continue;

            while (!isEmpty(queues[prio])) {
                allEmpty = 0;
                Process *p = depQueue(queues[prio]);
                int currentPid = p->pid;

                if (!first) printf(", ");
                printf("P%d", currentPid);
                first = 0;

                if (prio == 4) {
                    printf("[DEBUG] runTask2: P%d finished in Q5 (FCFS)\n", currentPid);
                    free(p);
                } else {
                    if (p->remaining_time <= quantums[prio]) {
                        printf("[DEBUG] runTask2: P%d finished in Q%d\n", currentPid, prio + 1);
                        free(p);
                    } else {
                        p->remaining_time -= quantums[prio];

                        int newPriority = priorities[currentPid];
                        if (newPriority < 5) {
                            newPriority++;
                            priorities[currentPid] = newPriority;
                        }
                        printf("[DEBUG] runTask2: P%d re-queued to Q%d remaining=%d\n",
                               currentPid, newPriority, p->remaining_time);

                        enterQueue(queues[newPriority - 1], currentPid,
                                 p->burst_time, p->remaining_time);
                        free(p);
                        break;
                    }
                }
            }

            if (!isEmpty(queues[prio])) break;
        }
    }

    printf("\n");
}
