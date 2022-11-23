<template>
  <a-layout id="app">
    <Menu />
    <a-layout :style="{ marginLeft: '0px' }">
      <ExplorerHeader
        v-if="hasExplorerHeader"
        @hide="onExplorerHeaderHide"
      />
      <BaiduNetdiskHeader v-if="hasBaiduNetdiskHeader" />
      <a-layout-content>
        <a-card class="view-wrapper">
          <router-view :key="$route.fullPath" />
        </a-card>
      </a-layout-content>
      <a-layout-footer>File Manager ©2020 Created by Arton</a-layout-footer>
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

html,body {
  height: 100vh;
}

#app,.ant-layout,.view-wrapper {
  height: 100%;
}

#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: #2c3e50;
}

.ant-card-body {
  height: 100%;
  padding: 12px;
}

.ant-drawer-body {
  padding: 5px 12px;
}

.ant-drawer-close {
  height: 30px;
  line-height: 30px;
  width: 30px;
}

.ant-drawer-header {
  padding: 5px 12px;
}

.ant-layout-content {
  height: 100%;
  margin: 8px 8px 0;
  overflow: initial;
}

.ant-layout-footer {
  padding: 3px 24px;
  text-align: center;
}

</style>
