<script>
import { baseUrl, baseGraphName } from '../constants'

export default {
  props: {
    visible: Boolean
  },
  data() {
    return {
      text: null
    }
  },
  mounted() {
    fetch(baseUrl + `${baseGraphName}/document/`)
      .then(res => res.json())
      .then(data => {
        this.text = data
      })
  },
  methods: {
    toggleVisibility(e) {
      if (e.target === e.currentTarget) {
        this.$emit("update:visible", !this.visible)
      }
    }
  }
}
</script>

<template>
  <div class="absolute top-0 left-0 w-full h-full flex justify-center items-center backdrop-blur-sm" v-show="visible" @click="toggleVisibility($event)">
    <div class="w-1/2 border border-neutral-700 filter-none">
      <h1 class="p-2 bg-white font-bold text-lg text-center">Document</h1>
      <p class="p-4 bg-slate-200">{{ text ? text : "Carregando..." }}</p>
    </div>
  </div>
</template>