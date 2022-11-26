<template>
  <div class="explorer">
    <a-row :gutter="[0, 16]">
      <a-col :span="12">
        <a-checkbox v-model="showthumb" @change="checkbox1Change">{{
          $t("setting.explorer.checkbox1")
        }}</a-checkbox>
      </a-col>
      <a-col :span="12">
        <a-checkbox v-model="cachethumb" @change="checkbox2Change">{{
          $t("setting.explorer.checkbox2")
        }}</a-checkbox>
      </a-col>
    </a-row>

    <a-row :gutter="[0, 16]">
      <a-col :span="4">
        <p class="label">{{ $t("setting.explorer.label2") }}</p>
      </a-col>
      <a-col :span="8">
        <a-select
          class="input"
          :default-value="thumbtype"
          @change="select1Change"
        >
          <a-select-option value="gif"> gif </a-select-option>
          <a-select-option value="webp"> webp </a-select-option>
        </a-select>
      </a-col>
      <a-col :span="4">
        <p class="label">{{ $t("setting.explorer.label3") }}</p>
      </a-col>
      <a-col :span="8">
        <a-input-number
          class="input"
          v-model="chunklimit"
          :min="0"
          @change="input2Change"
        />
      </a-col>
    </a-row>

    <a-row :gutter="[0, 16]">
      <a-col :span="4">
        <p class="label">{{ $t("setting.explorer.label1") }}</p>
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
      cachethumb: false,
      chunklimit: 10,
      thumbtype: "gif",
      exportpath: "",
    };
  },
  beforeMount() {
    const vm = this;
    vm.setting = vm.$store.state.setting;
    vm.showthumb = vm.setting.showthumb;
    vm.cachethumb = vm.setting.cachethumb;
    vm.chunklimit = vm.setting.chunklimit;
    vm.thumbtype = vm.setting.thumbtype;
    vm.exportpath = vm.setting.exportpath;
  },
  methods: {
    checkbox1Change(e) {
      const vm = this;
      vm.$store.commit("updateSetting", {
        showthumb: vm.showthumb,
      });
    },
    checkbox2Change(e) {
      const vm = this;
      vm.$store.commit("updateSetting", {
        cachethumb: vm.cachethumb,
      });
    },
    input1Change() {
      const vm = this;
      vm.$store.commit("updateSetting", { exportpath: vm.exportpath });
    },
    input2Change() {
      const vm = this;
      vm.$store.commit("updateSetting", {
        chunklimit: vm.chunklimit,
      });
    },
    select1Change(value) {
      const vm = this;
      vm.thumbtype = value;
      vm.$store.commit("updateSetting", {
        thumbtype: vm.thumbtype,
      });
    },
  },
};
</script>

<style scoped>
.explorer {
  padding-top: 20px;
}

.label {
  padding-top: 3px;
  text-align: left;
}

.input {
  min-width: calc(100% - 20px);
}
</style>