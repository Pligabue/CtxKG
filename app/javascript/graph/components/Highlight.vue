<script>
import { select, selectAll } from "d3"

export default {
  props: ["node", "synonymLink", "relationshipLink"],
  data() {
    return {
      text: null,
      prependedSvg: null
    }
  },
  watch: {
    node(newNode) {
      selectAll(".red-stroke").classed("red-stroke", false)
      let circle = select(`circle[index="${newNode.index}"]`).classed("red-stroke", true)
      this.text = newNode.label
      this.prependedSvg = `<circle r="8" fill="${circle.attr("fill")}" class="node-circle"></circle>`
    },
    synonymLink(newLink) {
      selectAll(".red-stroke").classed("red-stroke", false)
      select(`line.synonym[index="${newLink.index}"]`).classed("red-stroke", true)
      this.text = `${newLink.source.label} [${newLink.label}] ${newLink.target.label}`
      this.prependedSvg = null
    },
    relationshipLink(newLink) {
      selectAll(".red-stroke").classed("red-stroke", false)
      select(`line.relationship[index="${newLink.index}"]`).classed("red-stroke", true)
      this.text = `${newLink.source.label} [${newLink.label}] ${newLink.target.label}`
      this.prependedSvg = null
    }
  }
}
</script>

<template>
  <div class="absolute bottom-4 right-4 bg-white border-2 rounded-full border-blue-200 px-4 py-2 flex items-center" v-if="text">
    <svg v-if="prependedSvg" viewBox="-9 -9 18 18" class="inline-block w-5 h-5 mr-2" v-html="prependedSvg"></svg>
    <span class="font-semibold">{{ text }}</span>
  </div>
</template>