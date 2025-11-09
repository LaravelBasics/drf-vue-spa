// src/utils/file.js

/**
 * Content-Dispositionからファイル名抽出
 */
export function extractFilename(
    contentDisposition,
    defaultFilename = 'download',
) {
    if (!contentDisposition) return defaultFilename;

    const match = contentDisposition.match(
        /filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/,
    );
    if (match && match[1]) {
        return match[1].replace(/['"]/g, '');
    }

    return defaultFilename;
}

/**
 * Blobをダウンロード
 */
export function downloadBlob(blob, filename) {
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;

    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);

    window.URL.revokeObjectURL(url);
}

/**
 * APIレスポンスからCSVダウンロード
 */
export function downloadCSVFromResponse(
    response,
    defaultFilename = 'export.csv',
) {
    const filename = extractFilename(
        response.headers['content-disposition'],
        defaultFilename,
    );

    const blob = new Blob([response.data], {
        type: 'text/csv; charset=utf-8-sig',
    });

    downloadBlob(blob, filename);
}
