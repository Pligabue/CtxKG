<script>
import { select, selectAll } from "d3"

export default {
  props: ["highlight"],
  watch: {
    highlight() {
      selectAll(".red-stroke").classed("red-stroke", false)
      select(this.highlight).classed("red-stroke", true)
    }
  }
}
</script>

<template>
  <div class="absolute bottom-4 right-4 bg-white border-2 rounded-full border-blue-200 px-4 py-2" v-if="highlight">
    {{ highlight.dataset.label }}
  </div>
</template>