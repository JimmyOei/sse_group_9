# SSE Group 9: Measuring the Energy Cost of Merge Sort: Python vs. JavaScript


## Sorting Algorithms

In this project, we implemented three comparison-based sorting algorithms: **Merge Sort**, **Quick Sort** and **Heap Sort**. All algorithms were implemented independently in Python and JavaScript using the same structured pseudocode to ensure methodological consistency. By strictly following identical algorithmic steps, control flow, and data handling logic across languages, we ensure that any observed differences in execution time or energy consumption are attributable to the runtime environment rather than implementation discrepancies.

## Merge Sort – Pseudocode

```text
MERGE-SORT(A)
    if length(A) ≤ 1
        return A

    mid ← floor(length(A) / 2)

    left ← first half of A
    right ← second half of A

    sortedLeft ← MERGE-SORT(left)
    sortedRight ← MERGE-SORT(right)

    return MERGE(sortedLeft, sortedRight)


MERGE(left, right)
    result ← empty array
    i ← 0
    j ← 0

    while i < length(left) and j < length(right)
        if left[i] ≤ right[j]
            append left[i] to result
            i ← i + 1
        else
            append right[j] to result
            j ← j + 1

    append remaining elements of left (if any) to result
    append remaining elements of right (if any) to result

    return result
```


## Heap Sort – Pseudocode

```text
HEAP-SORT(A)
    n ← length(A)

    for i ← floor(n / 2) - 1 down to 0
        HEAPIFY(A, n, i)

    for i ← n - 1 down to 1
        swap A[0] and A[i]
        HEAPIFY(A, i, 0)


HEAPIFY(A, n, i)
    largest ← i
    left ← 2*i + 1
    right ← 2*i + 2

    if left < n and A[left] > A[largest]
        largest ← left

    if right < n and A[right] > A[largest]
        largest ← right

    if largest ≠ i
        swap A[i] and A[largest]
        HEAPIFY(A, n, largest)
```


## Running Instruction

Both the Python and JavaScript implementations require one mandatory command-line argument specifying the dataset size.

#### Available Dataset Sizes

The following dataset sizes are supported:

- 1000
- 10000
- 20000
- 50000
- 100000
- 125000
- 250000
- 1000000
- 4000000

The dataset size must be provided exactly as listed above.

### `python`

To run the Python implementation:

```bash
python merge_sort.py <dataset_size>
```

Example of command:

```bash
python merge_sort.py 1000
```

Make sure Python is installed and accessible from your command line:

```bash
python --version
```

### `JavaScript`

To run the JavaScript implementation, ensure that Node.js is installed.

You can verify the installation by running:

```bash
node -v
```

If a version number is displayed, Node.js is installed correctly.

Then execute:

```bash
node merge_sort.js <dataset_size>
```

Example

```bash
node merge_sort.js 1000
```


## Experiment Script
To run the experiment script, adjust the hardcoded parameters if needed, and then executed it with `sudo`:

```bash
sudo ./run_experiment.sh
```

The EnergiBridge csv results will be saved in the `results/` directory. Each run will generate a separate CSV file named according to the dataset size and implementation (e.g., `results/python_1000.csv` and `results/javascript_1000.csv`).