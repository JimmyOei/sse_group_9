#!/bin/bash

# Configuration of experiment
ENERGIBRIDGE_CMD="./EnergiBridge/target/release/energibridge"
NODE_CMD="node"
PYTHON_CMD="python3"
RESULTS_DIR="./results_MacOS_M1/quick_sort"  # output directory for results
ITERATIONS=10  # number of runs per dataset entry
COOLDOWN=10  # seconds between runs
PYTHON_SCRIPT="quick_sort.py" # merge_sort.py, heap_sort.py, quick_sort.py
JS_SCRIPT="quick_sort.js" # merge_sort.js, heap_sort.js, quick_sort.js
DATASET_FILES=(datasets/input-*.txt)

EXPERIMENT_START=$SECONDS

echo "============================================"
echo "  Running Experiment"
echo "============================================"
echo "Python version:  $($PYTHON_CMD --version)"
echo "Node version:    $($NODE_CMD --version)"
echo "Iterations per config: $ITERATIONS"
echo "Cooldown between runs: ${COOLDOWN}s"
echo "Dataset files: ${DATASET_FILES[*]}"
echo "Results directory: $RESULTS_DIR"
echo "============================================"
echo ""

TOTAL_RUNS=$(( ${#DATASET_FILES[@]} * 2 * ITERATIONS ))
CURRENT_RUN=0
FAILED_RUNS=()

for dataset_file in "${DATASET_FILES[@]}"; do
    # Extract the dataset size from filename (e.g. datasets/input-1000.txt -> 1000)
    dataset=$(basename "$dataset_file" .txt | sed 's/input-//')

    echo "--- Dataset size: $dataset ---"

    mkdir -p "$RESULTS_DIR/python/dataset_${dataset}"
    mkdir -p "$RESULTS_DIR/javascript/dataset_${dataset}"

    # Interleave Python and JavaScript runs to prevent ordering bias
    for i in $(seq 1 "$ITERATIONS"); do
        # Run Python version
        CURRENT_RUN=$((CURRENT_RUN + 1))
        OUTPUT_FILE="$RESULTS_DIR/python/dataset_${dataset}/run_${i}.csv"
        echo "[$CURRENT_RUN/$TOTAL_RUNS] Python | dataset=$dataset | run $i/$ITERATIONS"

        sudo "$ENERGIBRIDGE_CMD" \
            -o "$OUTPUT_FILE" \
            --summary \
            $PYTHON_CMD "$PYTHON_SCRIPT" "$dataset" > /dev/null 2>&1

        if [ $? -ne 0 ]; then
            echo "  WARNING: Run failed"
            FAILED_RUNS+=("Python | dataset=$dataset | run $i")
        fi

        # Cooldown between runs
        sleep "$COOLDOWN"

        # Run JavaScript version
        CURRENT_RUN=$((CURRENT_RUN + 1))
        OUTPUT_FILE="$RESULTS_DIR/javascript/dataset_${dataset}/run_${i}.csv"
        echo "[$CURRENT_RUN/$TOTAL_RUNS] JavaScript | dataset=$dataset | run $i/$ITERATIONS"

        sudo "$ENERGIBRIDGE_CMD" \
            -o "$OUTPUT_FILE" \
            --summary \
            $NODE_CMD "$JS_SCRIPT" "$dataset" > /dev/null 2>&1

        if [ $? -ne 0 ]; then
            echo "  WARNING: Run failed"
            FAILED_RUNS+=("JavaScript | dataset=$dataset | run $i")
        fi

        sleep "$COOLDOWN"
    done

    echo ""
done

EXPERIMENT_DURATION=$(( SECONDS - EXPERIMENT_START ))
EXPERIMENT_MINS=$(( EXPERIMENT_DURATION / 60 ))
EXPERIMENT_SECS=$(( EXPERIMENT_DURATION % 60 ))

echo "============================================"
echo "  Experiment complete!"
echo "  Total time: ${EXPERIMENT_MINS}m ${EXPERIMENT_SECS}s"
echo "  Results saved to: $RESULTS_DIR/"
if [ ${#FAILED_RUNS[@]} -gt 0 ]; then
    echo "Failed runs $(( ${#FAILED_RUNS[@]} )):"
    for failed in "${FAILED_RUNS[@]}"; do
        echo "  $failed"
    done
fi
echo "============================================"
