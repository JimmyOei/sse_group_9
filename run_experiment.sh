#!/bin/bash

# Configuration of experiment
ENERGIBRIDGE="./EnergiBridge/target/release/energibridge"
RESULTS_DIR="./results"  # output directory for results
ITERATIONS=2  # number of runs per dataset entry
COOLDOWN=10  # seconds between runs
PYTHON_SCRIPT="merge_sort.py"
JS_SCRIPT="merge_sort.js"
DATASET_FILES=(datasets/input-*.txt)

echo "============================================"
echo "  Running Experiment"
echo "============================================"
echo "Python version:  $(python3 --version)"
echo "Node version:    $(node --version)"
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

        sudo "$ENERGIBRIDGE" \
            -o "$OUTPUT_FILE" \
            --summary \
            python3 "$PYTHON_SCRIPT" "$dataset" > /dev/null 2>&1

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

        sudo "$ENERGIBRIDGE" \
            -o "$OUTPUT_FILE" \
            --summary \
            node "$JS_SCRIPT" "$dataset" > /dev/null 2>&1

        if [ $? -ne 0 ]; then
            echo "  WARNING: Run failed"
            FAILED_RUNS+=("JavaScript | dataset=$dataset | run $i")
        fi

        sleep "$COOLDOWN"
    done

    echo ""
done

echo "============================================"
echo "  Experiment complete!"
echo "  Results saved to: $RESULTS_DIR/"
if [ ${#FAILED_RUNS[@]} -gt 0 ]; then
    echo "Failed runs $(( ${#FAILED_RUNS[@]} )):"
    for failed in "${FAILED_RUNS[@]}"; do
        echo "  $failed"
    done
fi
echo "============================================"
