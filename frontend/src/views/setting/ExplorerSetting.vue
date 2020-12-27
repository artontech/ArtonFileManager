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
      <a-col :span="2"></a-col>
      <a-col :span="20"></a-col>
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
      showthumb: true
    };
  },
  beforeMount() {
    const vm = this;
    vm.setting = vm.$store.state.setting;
    vm.showthumb = vm.setting.showthumb;
  },
  methods: {
    checkbox1Change(e) {
      const vm = this;
      vm.$store.commit("updateSetting", { showthumb: vm.showthumb });
    }
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