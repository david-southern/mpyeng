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
    }
};
