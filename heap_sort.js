const fs = require("fs");

// ===== HEAP SORT IMPLEMENTATION ======

function heapify(arr, n, i) {

    let largest = i;
    let l = 2 * i + 1;
    let r = 2 * i + 2;

    if (l < n && arr[l] > arr[largest])
        largest = l;

    if (r < n && arr[r] > arr[largest])
        largest = r;

    if (largest != i) {
        [arr[i], arr[largest]] = [arr[largest], arr[i]];

        heapify(arr, n, largest);
    }
}

// Main function to do heap sort
function heapSort(arr) {
    let n = arr.length;

    for (let i = Math.floor(n / 2) - 1; i >= 0; i--)
        heapify(arr, n, i);

    for (let i = n - 1; i > 0; i--) {

        [arr[0], arr[i]] = [arr[i], arr[0]];

        heapify(arr, i, 0);
    }
}


function getValuesFromDataset(datasetName) {
    const data = fs.readFileSync("datasets/input-" + datasetName + ".txt", "utf8");
    const lines = data.split("\n");

    const numbers = [];
    for (let line of lines) {
        line = line.trim();
        if (line.length > 0) {
            numbers.push(parseInt(line, 10));
        }
    }

    return numbers;
}

function main() {
    if (process.argv.length !== 3) {
        console.log("Usage: node merge_sort.js <dataset_size>");
        process.exit(1);
    }

    const datasetName = process.argv[2];
    const values = getValuesFromDataset(datasetName);
    heapSort(values);
    console.log(values);
}

main();