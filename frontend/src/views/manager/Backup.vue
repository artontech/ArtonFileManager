<template>
  <div class="backup">
    <a-row>
      <a-button type="primary" :loading="btn1_loading" @click="btn1Click">{{
        $t("backup.btn1_caption")
      }}</a-button>
      
      <!-- Input import path -->
      <a-input
        class="path-input"
        size="large"
        :placeholder="$t('backup.edit1_placeholder')"
        v-model="path"
      >
        <a-icon slot="addonAfter" type="folder-open" />
      </a-input>
    </a-row>

    <!-- Progress dashboard -->
    <a-divider />
    <b>{{ $t("backup.label1_caption") }}</b>
    <a-divider />
    <a-row type="flex" justify="center">
      <a-col :span="8">
        <a-tooltip
          class="tooltip-structure"
          :title="$t('backup.tooltip1_caption')"
        >
          <a-progress
            type="dashboard"
            :percent="check_percent"
            :status="status"
          >
            <template #format="percent">
              <span>{{ $t("backup.progress1_caption") }}</span>
              <br />
              <span>{{ percent }}%</span>
            </template>
          </a-progress>
        </a-tooltip>
      </a-col>
      <a-col :span="8">
        <a-tooltip :title="$t('backup.tooltip2_caption')">
          <a-progress
            type="dashboard"
            :percent="upload_percent"
            :status="status"
          >
            <template #format="percent">
              <span>{{ $t("backup.progress2_caption") }}</span>
              <br />
              <span>{{ percent }}%</span>
            </template>
          </a-progress>
        </a-tooltip>
      </a-col>
    </a-row>

    <!-- Log -->
    <a-divider />
    <b>{{ $t("backup.label2_caption") }}</b>
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
      path: "",
      check_percent: 0,
      upload_percent: 0,
      status: null, // exception
      btn1_loading: false,
      msg: [],
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
    vm.websocket.connect(`ws://${vm.setting.address}/backup`);
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
      const body = {
        wid: vm.repository.wid,
        backup_path: vm.path,
      };
      vm.btn1_loading = true;
      const onError = () => {
        console.log(`[Error] failed to backup`);
        vm.btn1_loading = false;
      };
      vm.$http
        .post(`http://${vm.setting.address}/backup/copy`, body, options)
        .then((resp) => {
          vm.btn1_loading = false;
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

.path-input {
  margin-left: 15px;
  width: calc(100% - 110px);
}

</style>
