<script>
import { select, selectAll } from "d3"

export default {
  props: ["el", "type"],
  data() {
    return {
      text: null,
      prependedSvg: null
    }
  },
  watch: {
    el(newEl) {
      switch (this.type) {
        case "node":
          selectAll(".red-stroke").classed("red-stroke", false)
          let circle = select(`circle[index="${newEl.index}"]`).classed("red-stroke", true)
          this.text = newEl.label
          this.prependedSvg = `<circle r="8" fill="${circle.attr("fill")}" class="node-circle"></circle>`
          break;
        case "synonymLink":
          selectAll(".red-stroke").classed("red-stroke", false)
          select(`line.synonym[index="${newEl.index}"]`).classed("red-stroke", true)
          this.text = `${newEl.source.label} [${newEl.label}] ${newEl.target.label}`
          this.prependedSvg = null
          break;
        case "relationshipLink":
          selectAll(".red-stroke").classed("red-stroke", false)
          select(`line.relationship[index="${newEl.index}"]`).classed("red-stroke", true)
          this.text = `${newEl.source.label} [${newEl.label}] ${newEl.target.label}`
          this.prependedSvg = null
          break;
      }
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