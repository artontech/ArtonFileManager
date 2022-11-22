<template>
  <a-layout id="app">
    <Menu />
    <a-layout :style="{ marginLeft: '0px' }">
      <ExplorerHeader
        v-if="hasExplorerHeader"
        @hide="onExplorerHeaderHide"
      />
      <BaiduNetdiskHeader v-if="hasBaiduNetdiskHeader" />
      <a-layout-content :style="{ margin: '16px 16px 0', overflow: 'initial' }">
        <a-card class="view-wrapper" :style="{'--heightoffset': wrapperHeightOffset}">
          <router-view :key="$route.fullPath" />
        </a-card>
      </a-layout-content>
      <a-layout-footer :style="{ textAlign: 'center' }"
        >File Manager ©2020 Created by Arton</a-layout-footer
      >
    </a-layout>
  </a-layout>
</template>

<script>
export default {
  components: {
    Menu: () => import("@/components/Menu.vue"),
    ExplorerHeader: () => import("@/components/ExplorerHeader.vue"),
    BaiduNetdiskHeader: () => import("@/components/BaiduNetdiskHeader.vue"),
  },
  computed: {
    hasExplorerHeader() {
      const vm = this;
      const hasHeader = ["Explorer", "SearchFile"].indexOf(vm.$route.name) > -1;
      const result = vm.explorer_header_visible && hasHeader;
      if (!hasHeader) vm.explorer_header_visible = true;
      return result;
    },
    hasBaiduNetdiskHeader() {
      return ["BaiduSync"].indexOf(this.$route.name) > -1;
    },
    wrapperHeightOffset() {
      return this.hasExplorerHeader ? "100px" : "53px";
    },
  },
  data() {
    return {
      explorer_header_visible: true,
    };
  },
  methods: {
    onExplorerHeaderHide() {
      const vm = this;
      vm.explorer_header_visible = false;
    },
  },
};
</script>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: #2c3e50;
}

.ant-card-body {
  padding: 12px;
}

.ant-layout-footer {
  padding: 6px 24px;
}

.view-wrapper {
  min-height: calc(100vh - var(--heightoffset));
  max-height: calc(100vh - var(--heightoffset));
}
</style>
