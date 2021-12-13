<template>
  <div class="osssync">
    <a-button type="primary" :loading="btn1_loading" @click="btn1Click">{{
      $t("oss.osssync.btn1_caption")
    }}</a-button>

    <!-- Progress dashboard -->
    <a-divider />
    <b>{{ $t("oss.osssync.label1_caption") }}</b>
    <a-divider />
    <a-row type="flex" justify="center">
      <a-col :span="8">
        <a-tooltip
          class="tooltip-structure"
          :title="$t('oss.osssync.tooltip1_caption')"
        >
          <a-progress
            type="dashboard"
            :percent="check_percent"
            :status="status"
          >
            <template #format="percent">
              <span>{{ $t("oss.osssync.progress1_caption") }}</span>
              <br />
              <span>{{ percent }}%</span>
            </template>
          </a-progress>
        </a-tooltip>
      </a-col>
      <a-col :span="8">
        <a-tooltip :title="$t('oss.osssync.tooltip2_caption')">
          <a-progress
            type="dashboard"
            :percent="upload_percent"
            :status="status"
          >
            <template #format="percent">
              <span>{{ $t("oss.osssync.progress2_caption") }}</span>
              <br />
              <span>{{ percent }}%</span>
            </template>
          </a-progress>
        </a-tooltip>
      </a-col>
    </a-row>
  </div>
</template>

<script>
import options from "@/config/request";
import ArtonWebsocket from "@/util/ArtonWebsocket";

export default {
  data() {
    return {
      info: null,
      check_percent: 0,
      upload_percent: 0,
      status: null, // exception
      btn1_loading: false,
    };
  },
  beforeMount() {
    const vm = this;
    vm.repository = vm.$store.state.repository;
    vm.setting = vm.$store.state.setting;

    // Websocket
    vm.websocket = new ArtonWebsocket();
    vm.websocket.onMessage = (message) => {
      if (message.data) {
        const msg = JSON.parse(message.data);
        const data = msg?.data;
        switch (msg?.type) {
          case "check":
            if (msg.status == "success") {
              vm.check_percent = 100.0;
              vm.btn1_loading = true;
            }
            break;
          case "sync":
            const percent = (100.0 * data.now) / data.total;
            vm.check_percent = 100.0;
            vm.upload_percent = new Number(percent.toFixed(2));
            vm.btn1_loading = true;
            break;
          case "done":
            vm.check_percent = 100.0;
            vm.upload_percent = 100.0;
            vm.btn1_loading = false;
            break;
          default:
            console.log(msg);
            break;
        }
      }
    };
    vm.websocket.onOpen = () => {
      const ws_body = {
        type: "init",
        wid: vm.repository.wid,
      };
      vm.websocket.send(JSON.stringify(ws_body));
    };

    // Websocket onnect
    vm.websocket.connect(`ws://${vm.setting.address}/oss`);
  },
  beforeDestroy() {
    this.websocket?.close();
  },
  methods: {
    /* * * * * * * * Start: Trigger * * * * * * * */
    btn1Click() {
      const vm = this;
      const body = {
        wid: vm.repository.wid,
      };
      vm.btn1_loading = true;
      const onError = () => {
        console.log(`[Error] failed to sync oss`);
        vm.btn1_loading = false;
      };
      vm.$http
        .post(`http://${vm.setting.address}/oss/sync`, body, options)
        .then((resp) => {
          vm.switch1_loading = false;
          if (resp.body.status === "success") {
            console.log(resp.body);
          } else {
            onError();
          }
        }, onError);
    },
    /* * * * * * * * End: Trigger * * * * * * * */
  },
};
</script>

<style>
</style>
