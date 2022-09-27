const path = require("path");

module.exports = {
    mode: 'development',
    devtool: 'eval-source-map',
    module: {
        rules: [
            {
                test: /\.(ts)$/,
                exclude: /node_modules/,
                include: [path.resolve(__dirname, 'js')],
                use: 'ts-loader',
            }
        ]
    },
    resolve: {
        extensions: ['.ts', '.js'],
    },
    entry: {
        SSG: ['./js/SSG.ts']  
    },
    output: {
        path: path.resolve(__dirname, '../wwwroot/public'),
        filename: '[name]-bundle.js',
        library: "[name]"
    }
};
