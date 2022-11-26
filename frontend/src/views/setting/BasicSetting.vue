<template>
  <div class="basic">
    <a-row :gutter="[0,16]">
      <a-col :span="4">
        <p class="label">{{$t('setting.basic.label1')}}</p>
      </a-col>
      <a-col :span="20">
        <a-input-search
          size="large"
          :defaultValue="setting.address"
          :placeholder="$t('setting.basic.edit1_placeholder')"
          @search="connectServer"
        >
          <a-button
            slot="enterButton"
            :icon="btn1_icon"
            :loading="btn1_loading"
            :type="btn1_type"
          >{{$t('setting.basic.btn1_caption')}}</a-button>
        </a-input-search>
      </a-col>
    </a-row>
    <a-row :gutter="[0,16]">
      <a-col :span="4">
        <p class="label">{{$t('setting.basic.label2')}}</p>
      </a-col>
      <a-col :span="20">
        <a-input
          size="default"
          v-model="encrypt"
          :placeholder="$t('setting.basic.edit2_placeholder')"
          @change="input2Change"
          allowClear
        />
      </a-col>
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
      btn1_icon: "",
      btn1_loading: false,
      btn1_type: "primary",
      encrypt: ""
    };
  },
  beforeMount() {
    const vm = this;
    vm.setting = vm.$store.state.setting;
    vm.encrypt = vm.setting.encrypt;
  },
  methods: {
    connectServer(value) {
      const vm = this;
      vm.btn1_icon = "";
      vm.btn1_loading = true;
      vm.btn1_type = "primary";
      vm.$http.get(`http://${value}/workspace/ping`).then(
        resp => {
          vm.$store.commit("updateSetting", { address: value });
          vm.btn1_loading = false;
          vm.btn1_icon = "check-circle";
        },
        error => {
          console.log("[Error] failed to ping", value);
          vm.btn1_loading = false;
          vm.btn1_icon = "exclamation-circle";
          vm.btn1_type = "danger";
        }
      );
    },
    input2Change(e) {
      const vm = this;
      vm.$store.commit("updateSetting", { encrypt: vm.encrypt });
    }
  }
};
</script>

<style scoped>
.basic {
  padding-top: 20px;
}

.label {
  padding-top: 3px;
  text-align: left;
}
</style>