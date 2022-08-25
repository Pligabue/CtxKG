const { VueLoaderPlugin } = require('vue-loader')

module.exports = {
  mode: "production",
  entry: {
    graph: { import: "./graph", filename: "./results/graphs/index.js" }
  },
  output: {
    path: __dirname + "/static"
  },
  module: {
    rules: [
      {
        test: /\.vue$/,
        loader: 'vue-loader'
      },
      {
        test: /\.css$/,
        use: [
          'vue-style-loader',
          'css-loader'
        ]
      }
    ]
  },
  plugins: [
    new VueLoaderPlugin()
  ]
}