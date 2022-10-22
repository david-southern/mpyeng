const path = require('path');
const Handlebars = require("handlebars");
const HtmlWebpackPlugin = require('html-webpack-plugin');
const MiniCssExtractPlugin = require('mini-css-extract-plugin');

const packageJson = require('./package.json');
const packageVersion = (packageJson && packageJson.version) || '0.0.0';

module.exports = {
    mode: "development",
    devtool: 'inline-source-map',
    devServer: { static: './dist', },
    entry: {
        index: './src/ts/index.ts',
        style: './src/css/style.scss'
    },
    output: {
        path: path.resolve(__dirname, 'dist'),
        filename: '[name].bundle.js',
        clean: true
    },
    resolve: {
        extensions: ['.ts', '.js']
    },
    module: {
        rules: [
            { test: /\.ts$/, use: 'ts-loader', exclude: /node_modules/, },
            {
                test: /\.html$/i,
                loader: "html-loader",
                options: {
                    preprocessor: (content, loaderContext) => {
                        let result;

                        try {
                            result = Handlebars.compile(content)({
                                packageVersion,
                            });
                        } catch (error) {
                            loaderContext.emitError(error);

                            return content;
                        }

                        return result;
                    },
                },
            },
            {
                test: /\.scss$/i,
                use: [
                    // 'style-loader',
                    MiniCssExtractPlugin.loader,
                    'css-loader',
                    // 'sass-loader'
                    'resolve-url-loader',
                    {
                        loader: 'sass-loader',
                        options: {
                            sourceMap: true
                        }
                    }
                ]
            },
            { test: /\.(png|svg|jpg|jpeg|gif)$/i, type: 'asset/resource', },
            { test: /\.(woff|woff2|eot|ttf|otf)$/i, type: 'asset/resource', },
            { test: /\.(csv|tsv)$/i, use: ['csv-loader'], },
        ],
    },
    plugins: [
        new MiniCssExtractPlugin(),
        new HtmlWebpackPlugin({
            template: 'src/index.html',
            hash: true,
        })
    ],
    optimization: {
        runtimeChunk: 'single',
    },
};