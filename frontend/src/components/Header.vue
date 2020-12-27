<template>
  <a-layout-header class="header">
    <a-menu v-model="current" mode="horizontal">
      <a-menu-item key="file">
        <a-icon type="file" />文件管理
      </a-menu-item>
      <a-menu-item key="dup-file">
        <a-icon type="exception" />冗余文件
      </a-menu-item>
      <a-menu-item key="search-file">
        <a-icon type="file-search" />相似检索
      </a-menu-item>
    </a-menu>
  </a-layout-header>
</template>

<script>
export default {
  name: "Header",
  props: {},
  data() {
    return {
      current: ["file"]
    };
  },
  created() {},
  beforeUpdate() {},
  methods: {}
};
</script>

<style scoped>
.header {
  background: #fff;
  padding: 0 10px;
  box-shadow: 0 1px 4px rgba(0, 21, 41, 0.08);
}
</style>