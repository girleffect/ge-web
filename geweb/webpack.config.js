const path = require('path');


module.exports = {
    mode: process.env.NODE_ENV || "development",
    entry: {
        ninyampinga: path.join(__dirname, 'static/js', 'ninyampinga.js'),
        springster: path.join(__dirname, 'static/js', 'springster.js'),
        zathu: path.join(__dirname, 'static/js', 'zathu.js'),
    },
    devtool: "eval-source-map",
    output: { 
        path: path.join(__dirname, 'static/_dist'), 
        filename: '[name].bundle.js',
        clean: true
    },
    module: {
        rules: [
            {
                test: /\.s[ac]ss$/i,
                use: ['style-loader','css-loader', 'sass-loader']
            },
            { 
                test: /\.(jpg|jpeg|png|gif|mp3|svg)$/,
                use: ['file-loader'] 
            },
        ]
    }
}