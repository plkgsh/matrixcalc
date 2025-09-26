function parseMatrix(text) {
    return text.trim().split('\n').map(row => row.trim().split(/\s+/).map(Number));
}

function addMatrices() {
    const A = parseMatrix(document.getElementById('matrixA').value);
    const B = parseMatrix(document.getElementById('matrixB').value);

    if (A.length !== B.length || A[0].length !== B[0].length) {
        document.getElementById('result').textContent = "Ошибка: матрицы должны быть одинакового размера.";
        return;
    }

    const result = A.map((row, i) => row.map((val, j) => val + B[i][j]));
    displayResult(result);
}

function multiplyMatrices() {
    const A = parseMatrix(document.getElementById('matrixA').value);
    const B = parseMatrix(document.getElementById('matrixB').value);

    if (A[0].length !== B.length) {
        document.getElementById('result').textContent = "Ошибка: число столбцов матрицы A должно совпадать с числом строк матрицы B.";
        return;
    }

    const result = Array.from({length: A.length}, () => Array(B[0].length).fill(0));

    for (let i = 0; i < A.length; i++) {
        for (let j = 0; j < B[0].length; j++) {
            for (let k = 0; k < B.length; k++) {
                result[i][j] += A[i][k] * B[k][j];
            }
        }
    }

    displayResult(result);
}

function displayResult(matrix) {
    document.getElementById('result').textContent = matrix.map(row => row.join(' ')).join('\n');
}
