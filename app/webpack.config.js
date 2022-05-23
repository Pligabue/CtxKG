module.exports = {
  mode: "production",
  entry: {
    graph: { import: "./javascript/graph", filename: "./results/graphs/index.js" }
  },
  output: {
    path: __dirname + "/static"
  },
  watch: true
}