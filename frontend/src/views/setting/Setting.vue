<template>
  <div class="setting">
    <a-tabs :default-active-key="default_tab" tabPosition="left" @change="tabs1Change">
      <a-tab-pane key="tab1" :tab="$t('setting.tab1')">
        <BasicSetting />
      </a-tab-pane>
      <a-tab-pane key="tab2" :tab="$t('setting.tab2')" force-render>
        <ExplorerSetting />
      </a-tab-pane>
    </a-tabs>
  </div>
</template>

<script>
export default {
  name: "Setting",
  props: {},
  data() {
    return {
      setting: null,
      default_tab: "tab1"
    };
  },
  components: {
    BasicSetting: () => import("./BasicSetting"),
    ExplorerSetting: () => import("./ExplorerSetting")
  },
  beforeMount() {
    const vm = this;
    vm.setting = vm.$store.state.setting;
    let nocache = vm.setting.nocache;
    if (nocache?.default_tab !== undefined) {
      vm.default_tab = vm.setting.nocache.default_tab;
    }
  },
  methods: {
    tabs1Change(key) {
      const vm = this;
      vm.default_tab = key;
      vm.$store.commit("updateSettingNocache", {
        default_tab: key
      });
    }
  }
};
</script>

<style scoped>
.setting {
  padding-top: 10px;
}
</style>