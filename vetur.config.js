/** @type {import('vls').VeturConfig} */
module.exports = {
    projects: [
        {
            root: './frontend', // Vue プロジェクトのルートディレクトリ
            package: './package.json',
            tsconfig: './tsconfig.json',
        },
    ],
};
