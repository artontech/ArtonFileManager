<template>
  <div class="baidufix">
    <a-button type="primary" :loading="btn1_loading" @click="btn1Click">{{
      $t("baidunetdisk.baidufix.btn1_caption")
    }}</a-button>

    <!-- Progress dashboard -->
    <a-divider />
    <b>{{ $t("baidunetdisk.baidufix.label1_caption") }}</b>
    <a-divider />
    <a-row type="flex" justify="center">
      <a-col :span="8">
        <a-tooltip
          class="tooltip-structure"
          :title="$t('baidunetdisk.baidufix.tooltip1_caption')"
        >
          <a-progress
            type="dashboard"
            :percent="check_percent"
            :status="status"
          >
            <template #format="percent">
              <span>{{ $t("baidunetdisk.baidufix.progress1_caption") }}</span>
              <br />
              <span>{{ percent }}%</span>
            </template>
          </a-progress>
        </a-tooltip>
      </a-col>
      <a-col :span="8">
        <a-tooltip :title="$t('baidunetdisk.baidufix.tooltip2_caption')">
          <a-progress
            type="dashboard"
            :percent="upload_percent"
            :status="status"
          >
            <template #format="percent">
              <span>{{ $t("baidunetdisk.baidufix.progress2_caption") }}</span>
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
    vm.info = vm.$store.state.baidunetdisk.nocache.info;
    vm.user_info = vm.$store.state.baidunetdisk.user_info;

    if (!vm.info || !vm.user_info) {
      vm.$router.go("BaiduManager");
      return;
    }

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
          case "fix":
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
    vm.websocket.connect(`ws://${vm.setting.address}/baidunetdisk`);
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
        access_token: vm.info.access_token,
        upload_root: vm.info.upload_root,
      };
      vm.btn1_loading = true;
      const onError = () => {
        console.log(`[Error] failed to fix ${body.upload_root}`);
        vm.btn1_loading = false;
      };
      vm.$http
        .post(`http://${vm.setting.address}/baidunetdisk/fix`, body, options)
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