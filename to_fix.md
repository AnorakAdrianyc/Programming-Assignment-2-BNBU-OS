# Programming Assignment 2 - Items To Fix

## Logic Verification Required

### Task 1 Example 1

**Input:** P1=17, P2=15, P3=7
**Expected Output:** `P1, P2, P3, P1, P2, P3, P1, P2`
**Status:** Needs Testing

| Step | Queue | Action                          | Output |
| ---- | ----- | ------------------------------- | ------ |
| 1    | Q1    | P1 runs 4 (17→13), moves to Q2 | P1     |
| 2    | Q1    | P2 runs 4 (15→11), moves to Q2 | P2     |
| 3    | Q1    | P3 runs 4 (7→3), moves to Q2   | P3     |
| 4    | Q1    | Empty, check Q2                 | -      |
| 5    | Q2    | P1 runs 8 (13→5), moves to Q3  | P1     |
| 6    | Q2    | P2 runs 8 (11→3), moves to Q3  | P2     |
| 7    | Q2    | P3 runs 3 (completes)           | P3     |
| 8    | Q2    | Empty, check Q3                 | -      |
| 9    | Q3    | P1 runs 5 (completes)           | P1     |
| 10   | Q3    | P2 runs 3 (completes)           | P2     |

**Verify your code produces this exact sequence.**

---

### Task 1 Example 2

**Input:** P1=3, P2=10
**Expected Output:** `P1, P2, P2`
**Status:** Needs Testing

| Step | Queue | Action                         | Output |
| ---- | ----- | ------------------------------ | ------ |
| 1    | Q1    | P1 runs 3 (completes)          | P1     |
| 2    | Q1    | P2 runs 4 (10→6), moves to Q2 | P2     |
| 3    | Q1    | Empty, check Q2                | -      |
| 4    | Q2    | P2 runs 6 (completes in Q2)    | P2     |

---

### Task 2 Example

**Input:** Quantums: 6 4 8 7, P1=(24,1), P2=(10,5), P3=(17,3)
**Expected Output:** `P1, P1, P3, P1, P3, P1, P2, P3`
**Status:** Needs Testing

| Step | Current Queue | Process | Action                                | Output |
| ---- | ------------- | ------- | ------------------------------------- | ------ |
| 1    | Q1            | P1      | Runs 6 (24→18), priority 1→2, to Q2 | P1     |
| 2    | Q2            | P1      | Runs 4 (18→14), priority 2→3, to Q3 | P1     |
| 3    | Q3            | P3      | Runs 8 (17→9), priority 3→4, to Q4  | P3     |
| 4    | Q3            | P1      | Runs 8 (14→6), priority 3→4, to Q4  | P1     |
| 5    | Q4            | P3      | Runs 7 (9→2), priority 4→5, to Q5   | P3     |
| 6    | Q4            | P1      | Runs 6 (completes)                    | P1     |
| 7    | Q5            | P2      | Runs 10 (completes - FCFS)            | P2     |
| 8    | Q5            | P3      | Runs 2 (completes - FCFS)             | P3     |

**Note:** Verify this sequence matches your implementation.

---

## Code Issues to Address

### Issue #1: Task 2 Priority Tracking

**Location:** `runTask2()` function
**Problem:** Uses separate `priorities[]` array instead of storing priority in `Process` struct
**Impact:** Works functionally but may not match assignment expectations
**Suggested Fix:** Add `priority` field to `Process` struct for Task 2

```c
typedef struct Process {
    int pid;
    int burst_time;
    int remaining_time;
    int priority;          // Add this for Task 2
    struct Process *next;
} Process;
```

---

### Issue #2: scanf Newline Buffer

**Location:** All `scanf()` calls in `runTask1()` and `runTask2()`
**Problem:** Newline character remains in input buffer
**Impact:** May cause issues with subsequent character input
**Suggested Fix:** Add space before format specifier or consume newline

```c
// Option 1: Add space
scanf(" %d", &numProcesses);

// Option 2: Consume newline after
scanf("%d", &numProcesses);
getchar();  // or while(getchar() != '\n');
```

---

### Issue #3: Memory Cleanup Missing in Task 2

**Location:** End of `runTask2()` function
**Problem:** No queue cleanup like in Task 1
**Impact:** Minor memory leak
**Suggested Fix:** Add cleanup code before function exit

```c
// Add at end of runTask2(), before closing brace:
for (int i = 0; i < 5; i++) {
    // Free all processes in queue
    Process *current = queues[i]->front;
    while (current != NULL) {
        Process *temp = current;
        current = current->next;
        free(temp);
    }
    free(queues[i]);
}
```

---

### Issue #4: Potential Missing .h File

**Location:** Project root
**Problem:** Assignment says "At the beginning of all .c and .h files"
**Impact:** May need separate header file for full credit
**Suggested Action:** Check with instructor if header file is required

---

## Testing Checklist

- [ ] Compile without warnings: `gcc startUp.c -o startUp -Wall`
- [ ] Test Task 1 Example 1 produces: `P1, P2, P3, P1, P2, P3, P1, P2`
- [ ] Test Task 1 Example 2 produces: `P1, P2, P2`
- [ ] Test Task 2 example produces: `P1, P1, P3, P1, P3, P1, P2, P3`
- [ ] Test menu system (0 exits, 1 runs Task 1, 2 runs Task 2)
- [ ] Test invalid menu input shows: "Please enter 0, 1 or 2."
- [ ] Verify no crashes on edge cases (1 process, all same burst time, etc.)

---

## Questions for Instructor

1. Should the `Process` struct include a `priority` field for Task 2?
2. Is a separate `.h` header file required, or is single `.c` file acceptable?
3. Are there any specific edge cases that will be tested?

---

## Submission Checklist

- [ ] File header complete with author, student ID, date, purpose
- [ ] All `.c` and `.h` files (if applicable) ready
- [ ] Code compiles without errors
- [ ] All example outputs match exactly
- [ ] No debug print statements left in code
- [ ] Memory properly freed (no leaks)
- [ ] Missing record.txt with sample data in the format name score (per line)
