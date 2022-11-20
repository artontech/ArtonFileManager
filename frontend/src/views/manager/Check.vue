<template>
  <div class="check">
    <a-row>
      <a-button type="primary" v-if="!checking" @click="btn1Click">{{
        $t("check.btn1_caption")
      }}</a-button>
      <a-button type="danger" v-else @click="btn2Click">{{
        $t("all.cancel")
      }}</a-button>

      <a-date-picker class="date-picker" @change="picker1Change" />
    </a-row>

    <!-- Progress dashboard -->
    <a-divider />
    <b>{{ $t("check.label1_caption") }}</b>
    <a-divider />
    <a-row type="flex" justify="center">
      <a-col :span="8">
        <a-tooltip
          class="tooltip-structure"
          :title="$t('check.tooltip1_caption')"
        >
          <a-progress
            type="dashboard"
            :percent="check_percent"
            :status="status"
          >
            <template #format="percent">
              <span>{{ $t("check.progress1_caption") }}</span>
              <br />
              <span>{{ percent }}%</span>
            </template>
          </a-progress>
        </a-tooltip>
      </a-col>
      <a-col :span="8">
        <a-tooltip :title="$t('check.tooltip2_caption')">
          <a-progress
            type="dashboard"
            :percent="upload_percent"
            :status="status"
          >
            <template #format="percent">
              <span>{{ $t("check.progress2_caption") }}</span>
              <br />
              <span>{{ percent }}%</span>
            </template>
          </a-progress>
        </a-tooltip>
      </a-col>
    </a-row>

    <!-- Log -->
    <a-divider />
    <b>{{ $t("check.label2_caption") }}</b>
    <a-divider />
    <div class="logging-wrapper">
      <a-list item-layout="horizontal" size="small" :data-source="msg">
        <a-list-item slot="renderItem" slot-scope="item">
          <span>{{ item }}</span>
        </a-list-item>
      </a-list>
    </div>
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
      checking: false,
      msg: [],
      check_date: "",
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
              vm.checking = true;
            }
            break;
          case "sync":
            const percent = (100.0 * data.now) / data.total;
            vm.check_percent = 100.0;
            vm.upload_percent = new Number(percent.toFixed(2));
            vm.checking = true;
            break;
          case "cancel":
            console.log(msg?.status);
            if (msg?.status == "run") {
              vm.$message.warning(vm.$i18n.t("all.canceling"));
            } else if (msg?.status == "success") {
              vm.checking = false;
              vm.$message.success(vm.$i18n.t("all.canceled"));
            }
            break;
          case "done":
            vm.check_percent = 100.0;
            vm.upload_percent = 100.0;
            vm.checking = false;
            break;
          case "msg":
            vm.addMsg(vm.$i18n.t("all.info") + ": " + data?.msg);
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
    vm.websocket.connect(`ws://${vm.setting.address}/check`);
  },
  beforeDestroy() {
    const vm = this;
    vm.websocket?.close();
    vm.msg.splice(0, vm.msg.length);
    vm.path = "";
  },
  methods: {
    addMsg(data) {
      const vm = this;
      if (vm.msg.length > 100) {
        vm.msg.splice(0, 1);
      }
      vm.msg.push(data);
    },
    /* * * * * * * * Start: Trigger * * * * * * * */
    btn1Click() {
      const vm = this;
      if (!vm.check_date) {
        vm.$message.error(vm.$i18n.t("check.no_check_date"));
        return;
      }
      const body = {
        wid: vm.repository.wid,
        check_date: vm.check_date,
      };
      vm.checking = true;
      const onError = () => {
        console.log(`[Error] failed to check`);
        vm.checking = false;
      };
      vm.$http
        .post(`http://${vm.setting.address}/check/check`, body, options)
        .then((resp) => {
          vm.checking = false;
          if (resp.body.status === "success") {
            console.log(resp.body);
          } else {
            onError();
          }
        }, onError);
    },
    btn2Click() {
      const vm = this;
      const ws_body = {
        type: "cancel",
        wid: vm.repository.wid,
      };
      vm.websocket.send(JSON.stringify(ws_body));
    },
    picker1Change(date, dateString) {
      date;
      this.check_date = dateString;
    },
    /* * * * * * * * End: Trigger * * * * * * * */
  },
};
</script>

<style>

.date-picker {
  margin-left: 20px;
}

</style>
