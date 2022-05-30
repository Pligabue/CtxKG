const { VueLoaderPlugin } = require('vue-loader')

module.exports = {
  mode: "production",
  entry: {
    graph: { import: "./javascript/graph", filename: "./results/graphs/index.js" }
  },
  output: {
    path: __dirname + "/static"
  },
  module: {
    rules: [
      {
        test: /\.vue$/,
        loader: 'vue-loader'
      }
    ]
  },
  plugins: [
    new VueLoaderPlugin()
  ]
}