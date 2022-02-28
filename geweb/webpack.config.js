const path = require("path"),
MiniCssExtractPlugin = require("mini-css-extract-plugin"),
    globImporter = require("node-sass-glob-importer");


module.exports = {
    mode: process.env.NODE_ENV || "development",
    entry: {
        ninyampinga: path.join(__dirname, "static/js", "ninyampinga.js"),
        springster: path.join(__dirname, "static/js", "springster.js"),
        tujibebe: path.join(__dirname, "static/js", "tujibebe.js"),
        yegna: path.join(__dirname, "static/js", "yegna.js"),
        zathu: path.join(__dirname, "static/js", "zathu.js"),
    },
    devtool: "eval-source-map",
    output: { 
        path: path.join(__dirname, "static/_dist"), 
        filename: "[name].bundle.js",
        clean: true
    },
    
    module: {
        rules: [
            {
                test: /\.s[ac]ss$/i,
                use: [
                    "style-loader",
                    {
                        loader: MiniCssExtractPlugin.loader,
                        options: {
                            esModule: false,
                        }
                    },
                    "css-loader",
                    {
                        loader: "sass-loader",
                        options: {
                            sassOptions: {
                              importer: globImporter()
                            }
                        }
                    }
                ]
            },
            { 
                test: /\.(jpg|jpeg|png|gif|mp3|svg)$/,
                use: [ "file-loader"] 
            },
        ]
    },
    plugins: [
        new MiniCssExtractPlugin()
    ]
}