<template>
  <div class="explorer">
    <a-row>
      <a-col :span="1"></a-col>
      <a-col :span="20">
        <a-checkbox
          v-model="showthumb"
          @change="checkbox1Change"
        >{{$t('setting.explorer.checkbox1')}}</a-checkbox>
      </a-col>
      <a-col :span="1"></a-col>
    </a-row>
    <a-row :gutter="[0,16]">
      <a-col :span="1"></a-col>
      <a-col :span="2">
        <p class="label">{{$t('setting.explorer.label1')}}</p>
      </a-col>
      <a-col :span="20">
        <a-input
          size="default"
          v-model="exportpath"
          :placeholder="$t('setting.explorer.edit1_placeholder')"
          @change="input1Change"
          allowClear
        />
      </a-col>
      <a-col :span="1"></a-col>
    </a-row>
  </div>
</template>

<script>
export default {
  name: "BasicSetting",
  props: {},
  data() {
    return {
      setting: null,
      showthumb: true,
      exportpath: "",
    };
  },
  beforeMount() {
    const vm = this;
    vm.setting = vm.$store.state.setting;
    vm.showthumb = vm.setting.showthumb;
    vm.exportpath = vm.setting.exportpath;
  },
  methods: {
    checkbox1Change(e) {
      const vm = this;
      vm.$store.commit("updateSetting", { showthumb: vm.showthumb });
    },
    input1Change() {
      const vm = this;
      vm.$store.commit("updateSetting", { exportpath: vm.exportpath });
    },
  }
};
</script>

<style scoped>
.explorer {
  padding-top: 20px;
}

.label {
  padding-top: 3px;
  text-align: center;
}
</style>