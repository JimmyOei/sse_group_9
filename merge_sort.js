const fs = require("fs");

// ===== MERGE SORT IMPLEMENTATION ======

function mergeSort(arr) {
    if (arr.length <= 1) {
        return arr;
    }

    const mid = Math.floor(arr.length / 2);
    const leftHalf = arr.slice(0, mid);
    const rightHalf = arr.slice(mid);

    const sortedLeft = mergeSort(leftHalf);
    const sortedRight = mergeSort(rightHalf);

    return merge(sortedLeft, sortedRight);
}

function merge(left, right) {
    const result = [];
    let i = 0;
    let j = 0;

    while (i < left.length && j < right.length) {
        if (left[i] <= right[j]) {
            result.push(left[i]);
            i++;
        } else {
            result.push(right[j]);
            j++;
        }
    }

    while (i < left.length) {
        result.push(left[i]);
        i++;
    }

    while (j < right.length) {
        result.push(right[j]);
        j++;
    }

    return result;
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
    console.log(mergeSort(values));
}

main();
