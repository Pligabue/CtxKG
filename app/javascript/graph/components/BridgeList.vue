<script>
export default {
  props: ["baseUrl", "node"],
  emits: ["expandNode"],
  data() {
    return {
      bridges: {},
      show: false,
      loading: false
    }
  },
  watch: {
    node(newNode) {
      if (newNode) {
        this.loading = true
        fetch(this.baseUrl + `${newNode.graph}/bridges/${newNode.id}/`)
          .then(res => res.json())
          .then(data => {
            this.bridges = data
            this.show = true
          })
          .finally(() => {
            this.loading = false
          })
      } else {
        this.show = false
      }
    }
  },
  methods: {
    expandNode(graphName, nodeId) {
      fetch(this.baseUrl + `${graphName}/${nodeId}/`)
        .then(res => res.json())
        .then(data => {
          let { entities, graph, links } = data

          let expandedNodes = Object.entries(entities)
            .filter(([id, label]) => id !== nodeId)
            .map(([id, label]) => ({ id: id, label: label, graph: graphName }))
          let expandedRelationshipLinks = graph
            .map(({ subject_id, relation, object_id }) => ({ source: subject_id, target: object_id, label: relation }))
          let expandedSynonymLinks = Object.entries(links)
            .flatMap(([entity, links]) => links.map((link) => ({ source: entity, target: link, label: "=" })))
            .filter((link, index, arr) => index === arr.findIndex((el) => (el.source === link.source && el.target === link.target) || (el.source === link.target && el.target === link.source)))
          
          this.$emit("expandNode", nodeId, {
            nodes: expandedNodes,
            relationshipLinks: expandedRelationshipLinks,
            synonymLinks: expandedSynonymLinks
          })
        })
    },
    linkTo(graph) {
      return this.baseUrl + `${graph}/`
    }
  }
}
</script>

<template>
  <div class="absolute border border-neutral-700 bg-white top-0 right-10" v-if="show">
    <h1 class="p-2 pt-3 font-semibold text-center">Pontes</h1>
    <div class="bg-slate-200 max-h-60 overflow-auto">
      <template v-if="loading">
        <div class="py-2 px-3 border-t border-neutral-400 flex items-center">
          <span class="text-sm flex-grow">Carregando...</span>
        </div>
      </template>
      <template v-else-if="Object.keys(bridges).length > 0">
        <div class="py-2 px-3 border-t border-neutral-400 flex items-center" v-for="(nodeId, graph) in bridges">
          <span class="text-sm flex-grow">{{ graph.replace(".json", "") }}</span>
          <i class="fas fa-code-branch mx-2" @click="expandNode(graph, nodeId)"></i>
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