<script>
export default {
  props: ["baseGraphName", "node"],
  data() {
    return {
      baseBridgeUrl: window.location.pathname + "bridges/",
      bridges: {},
      show: false
    }
  },
  watch: {
    node(newNode) {
      if (newNode) {
        fetch(this.baseBridgeUrl + newNode.id)
          .then(res => res.json())
          .then(data => {
            this.bridges = data
            this.show = true
          })
      } else {
        this.show = false
      }
    }
  },
  methods: {
    linkTo(graph) {
      return window.location.pathname.replace(this.baseGraphName, graph)
    }
  }
}
</script>

<template>
  <div class="absolute border border-neutral-700 bg-white top-0 right-10" v-if="show">
    <h1 class="p-2 pt-3 font-semibold text-center">Pontes</h1>
    <div class="bg-slate-200 max-h-60 overflow-auto">
      <template v-if="Object.keys(bridges).length > 0">
        <div class="py-2 px-3 border-t border-neutral-400 flex items-center" v-for="(node, graph) in bridges">
          <span class="text-sm flex-grow">{{ graph.replace(".json", "") }}</span>
          <i class="fas fa-code-branch mx-2"></i>
          <a :href="linkTo(graph)" target="_blank">
            <i class="fas fa-level-up-alt"></i>
          </a>
        </div>
      </template>
      <template v-else>
        <div class="py-2 px-3 border-t border-neutral-400 flex items-center">
          <span class="text-sm flex-grow">Sem pontes.</span>
        </div>
      </template>
    </div>
  </div>
</template>