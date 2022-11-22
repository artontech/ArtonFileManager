<template>
  <a-layout-header class="explorerheader">
    <a-row>
      <a-col :span="20">
        <a-menu mode="horizontal" :selectedKeys="[selected]">
          <a-menu-item key="Explorer" v-on:click="go">
            <a-icon type="file" />文件管理
          </a-menu-item>
          <a-menu-item key="SearchFile" v-on:click="go">
            <a-icon type="file-search" />{{ $t("menu.search_file") }}
          </a-menu-item>
          <a-menu-item key="DupFile" v-on:click="go">
            <a-icon type="exception" />冗余文件
          </a-menu-item>
        </a-menu>
      </a-col>
      <a-col :span="4" :style="{ textAlign: 'right', lineHeight: '47px' }">
        <a @click="hide">
          <a-icon type="caret-up" />{{ $t("all.hide") }}
        </a>
      </a-col>
    </a-row>
  </a-layout-header>
</template>

<script>
export default {
  name: "ExplorerHeader",
  props: {},
  data() {
    return {
      selected: "Explorer",
    };
  },
  created() {
    const vm = this;
    if (vm.$route.name) vm.selected = vm.$route.name;
    vm.$router.beforeResolve((to, from, next) => {
      vm.selected = to.name;
      next();
    });
  },
  beforeUpdate() {},
  methods: {
    go(item) {
      this.$router.go(item.key);
    },
    hide() {
      this.$emit("hide");
    },
  },
};
</script>

<style scoped>
.explorerheader {
  background: #fff;
  height: 47px;
  padding: 0 10px;
  box-shadow: 0 1px 4px rgba(0, 21, 41, 0.08);
}
</style>