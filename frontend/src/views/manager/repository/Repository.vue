<template>
  <div>
    <a-row>
      <a-col>
        <a-input
          size="large"
          v-model="repository.path"
          :addon-before="$t('repository.edit1_addonbefore')"
          :defaultValue="repository.path"
          :placeholder="$t('repository.edit1_placeholder')"
        >
          <a-icon slot="addonAfter" type="folder-open" />
        </a-input>
      </a-col>
    </a-row>
    <a-row type="flex" justify="space-around">
      <a-col :span="4">
        {{$t('repository.label1_caption')}}
        <a-switch
          :checked="switch1_checked"
          :disabled="switch1_disabled"
          :loading="switch1_loading"
          @change="switch1Change"
        >
          <a-icon slot="checkedChildren" type="check" />
          <a-icon slot="unCheckedChildren" type="close" />
        </a-switch>
      </a-col>
      <a-col :span="4">
        <a-button
          size="small"
          :disabled="btn1_disabled || switch1_checked"
          :icon="btn1_icon"
          :loading="btn1_loading"
          :type="btn1_type"
          @click="btn1Click"
        >{{$t('repository.btn1_caption')}}</a-button>
      </a-col>
    </a-row>
  </div>
</template>

<script>
import options from "@/config/request";

export default {
  name: "Repository",
  props: {},
  data() {
    return {
      repository: null,
      setting: null,
      btn1_disabled: false,
      btn1_icon: "",
      btn1_loading: false,
      btn1_type: "primary",
      switch1_checked: false,
      switch1_disabled: false,
      switch1_loading: false
    };
  },
  beforeMount() {
    this.repository = this.$store.state.repository;
    this.setting = this.$store.state.setting;

    this.switch1_checked = this.repository.loaded;
  },
  methods: {
    switch1Change(checked, event) {
      const vm = this;

      // clear nocache info
      vm.$store.commit("updateExplorer", {
        nocache: undefined
      });

      vm.$store.commit("updateRepository", {
        path: vm.repository.path
      });
      vm.switch1_checked = checked;
      vm.switch1_loading = true;
      const instruction = checked ? "open" : "close";
      const body = {
        path: vm.repository.path,
        wid: vm.repository.wid
      };
      vm.$http
        .post(
          `http://${vm.setting.address}/workspace/${instruction}`,
          body,
          options
        )
        .then(
          resp => {
            vm.switch1_loading = false;
            if (resp.body.status === "success") {
              vm.$store.commit("updateRepository", {
                loaded: checked,
                wid: resp.body.data?.wid
              });
            } else {
              if (checked) {
                // Failed to open
                vm.switch1_checked = false;
              } else {
                vm.$store.commit("updateRepository", {
                loaded: false,
                wid: undefined
              });
              }
            }
          },
          error => {
            console.log(
              `[Error] failed to ${instruction} workspace ${body.path}`
            );
            vm.switch1_loading = false;
            vm.switch1_checked = !checked;
          }
        );
    },
    btn1Click(event) {
      const vm = this;

      vm.$store.commit("updateRepository", {
        init: false,
        path: vm.repository.path
      });
      vm.btn1_icon = "";
      vm.btn1_loading = true;
      vm.btn1_type = "primary";
      const body = {
        path: vm.repository.path
      };
      const onError = () => {
        console.log(`[Error] failed to init workspace ${body.path}`);
        vm.btn1_disabled = false;
        vm.btn1_icon = "exclamation-circle";
        vm.btn1_loading = false;
        vm.btn1_type = "danger";
      };
      vm.$http
        .post(`http://${vm.setting.address}/workspace/init`, body, options)
        .then(
          resp => {
            vm.btn1_loading = false;
            if (resp.body.status === "success") {
              vm.$store.commit("updateRepository", {
                init: true
              });
              vm.btn1_disabled = true;
              vm.btn1_icon = "check-circle";
            } else {
              onError();
            }
          },
          error => {
            onError();
          }
        );
    }
  }
};
</script>

<style scoped>
.ant-row {
  margin: 16px 0;
}
</style>