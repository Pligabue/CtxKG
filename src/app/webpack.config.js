const { VueLoaderPlugin } = require('vue-loader')

module.exports = {
  mode: "production",
  entry: "./graph",
  output: {
    path: __dirname + "/static",
    filename: 'vue.js'
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