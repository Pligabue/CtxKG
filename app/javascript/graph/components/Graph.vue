<script>
import * as d3 from "d3"

import { buildColors } from "../colors"

export default {
  props: {
    showText: Boolean,
    overallStrength: Number,
    synonymStrength: Number,
    relationshipStrength: Number,
    colorVariation: Number
  },
  data() {
    return {
      baseGraphUrl: window.location.pathname + "json",
      title: "",
      nodes: [],
      relationshipLinks: [],
      synonymLinks: [],
      graph: null,
      radius: 8
    }
  },
  mounted() {
    this.setupGraph()
    window.d3 = d3
  },
  watch: {
    nodes() {
      this.updateGraph()
    },
    colorVariation() {
      this.updateColors()
    }
  },
  methods: {
    updateGraph() {
      const svg = d3.select("#graph-svg")

      const nodes = svg.selectAll("g")
      const nodeEnter = nodes.data(this.nodes).enter().append("g")
      nodeEnter.attr("data-entity", d => d.label).attr("data-id", d => d.id)
      nodeEnter.append("text").text(d => d.label).classed("node-text", true)
      nodeEnter.append("circle").classed("node-circle", true).attr("r", this.radius).attr("data-id", d => d.id)
      nodes.data(this.nodes).exit().remove()
      
      const relationshipLinks = svg.selectAll("line.relationship").data(this.relationshipLinks)
      relationshipLinks.enter().append("line").attr("stroke-width", 1).classed("relationship", true)
      relationshipLinks.exit().remove()
      
      
      const synonymLinks = svg.selectAll("line.synonym").data(this.synonymLinks)
      synonymLinks.enter().append("line").attr("stroke-width", 2).classed("synonym", true)
      synonymLinks.exit().remove()

      this.updateColors()
    },
    setupGraph() {
      fetch(this.baseGraphUrl)
        .then(res => res.json())
        .then(data => {
          let { documents, entities, graph, links } = data
          this.title = documents.join(", ")
          this.nodes = Object.entries(entities).map(([id, label]) => ({ id: id, label: label }))
          this.relationshipLinks = graph.map(({ subject_id, relation, object_id }) => ({ source: subject_id, target: object_id, label: relation }))
          this.synonymLinks = Object.entries(links)
            .flatMap(([entity, links]) => links.map((link) => ({ source: entity, target: link, label: ">" })))
            .filter((link, index, arr) => index === arr.findIndex((el) => (el.source === link.source && el.target === link.target) || (el.source === link.target && el.target === link.source)))
        })
    },
    updateColors() {
      let colors = buildColors(this.nodes, this.colorVariation)
      d3.selectAll("g").data(this.nodes).selectAll("circle").datum(d => d).style("fill", d => (console.log(d), colors[d.id]))
    }
  }
}
</script>

<template>
  <svg id="graph-svg" class="graph-svg"></svg>
</template>