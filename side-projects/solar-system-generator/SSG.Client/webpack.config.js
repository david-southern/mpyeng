const webpack = require("webpack");
const CopyPlugin = require("copy-webpack-plugin");
const path = require("path");

module.exports = {
    mode: 'development',
    devtool: 'eval-source-map',
    module: {
        rules: [
            {
                test: /\.([jt]s)$/,
                exclude: /node_modules/,
                include: [path.resolve(__dirname, 'wwwroot/js')],
                use: 'ts-loader',
            }
        ]
    },
    resolve: {
        extensions: ['.ts', '.js'],
    },
    entry: {
        SSG: ['./wwwroot/js/SSG.ts']
    },
    output: {
        path: path.resolve(__dirname, './wwwroot/public'),
        filename: '[name]-bundle.js',
        library: "[name]"
    },
    plugins: [
        new webpack.DefinePlugin({
            'process.browser': 'true'
        }),
        new CopyPlugin({
            patterns: [
                { from: "node_modules/jimp/browser/lib/jimp.js", to: "public/jimp.js" },
            ],
        }),
    ],
};
