<template>
  <a-layout-header class="baidunetdiskheader">
    <a-menu v-model="current" mode="horizontal">
      <a-menu-item key="sync">
        <a-icon type="cloud-sync" />文件同步
      </a-menu-item>
      <a-menu-item key="file">
        <a-icon type="file" />文件管理
      </a-menu-item>
    </a-menu>
  </a-layout-header>
</template>

<script>
export default {
  name: "BaiduNetdiskHeader",
  props: {},
  data() {
    return {
      current: ["sync"]
    };
  },
  created() {},
  beforeUpdate() {},
  methods: {}
};
</script>

<style scoped>
.baidunetdiskheader {
  background: #fff;
  padding: 0 10px;
  box-shadow: 0 1px 4px rgba(0, 21, 41, 0.08);
}
</style>