<template>
  <a-drawer
    placement="right"
    width="50vw"
    :closable="true"
    :maskClosable="false"
    :title="$t('explorer.import_drawer.title')"
    :visible="visible"
    :after-visible-change="afterVisibleChange"
    @close="onClose"
  >
    <!-- Input import path -->
    <a-input
      size="large"
      :placeholder="$t('explorer.import_drawer.edit1_placeholder')"
      v-model="path"
    >
      <a-icon slot="addonAfter" type="folder-open" />
    </a-input>

    <!-- Progress dashboard -->
    <a-divider />
    <b>{{ $t("explorer.import_drawer.label1_caption") }}</b>
    <a-divider />
    <a-row type="flex" justify="center">
      <a-col :span="8">
        <a-tooltip
          class="tooltip-structure"
          :title="$t('explorer.import_drawer.tooltip1_caption')"
        >
          <a-progress
            type="dashboard"
            :percent="structure_percent"
            :status="status"
          >
            <template #format="percent">
              <span>{{ $t("explorer.import_drawer.progress1_caption") }}</span>
              <br />
              <span>{{ percent }}%</span>
            </template>
          </a-progress>
        </a-tooltip>
      </a-col>
      <a-col :span="8">
        <a-tooltip :title="$t('explorer.import_drawer.tooltip2_caption')">
          <a-progress
            type="dashboard"
            :percent="files_percent"
            :status="status"
          >
            <template #format="percent">
              <span>{{ $t("explorer.import_drawer.progress2_caption") }}</span>
              <br />
              <span>{{ percent }}%</span>
            </template>
          </a-progress>
        </a-tooltip>
      </a-col>
    </a-row>

    <!-- Log -->
    <a-divider />
    <b>{{ $t("explorer.import_drawer.label2_caption") }}</b>
    <a-divider />
    <div class="logging-wrapper">
      <a-list item-layout="horizontal" size="small" :data-source="msg">
        <a-list-item slot="renderItem" slot-scope="item">
          <span>{{ item }}</span>
        </a-list-item>
      </a-list>
    </div>
    <a-divider />
    <div id="btn-wrapper">
      <a-button
        :disabled="btn1_disabled"
        :icon="btn1_icon"
        :loading="btn1_loading"
        :type="btn1_type"
        @click="btn1Click"
        >{{ $t("all.import") }}</a-button
      >
    </div>
  </a-drawer>
</template>

<script>
import options from "@/config/request";
import ArtonWebsocket from "@/util/ArtonWebsocket";

export default {
  data() {
    return {
      repository: null,
      setting: null,
      websocket: null,
      path: "",
      btn1_disabled: false,
      btn1_icon: "",
      btn1_loading: false,
      btn1_type: "primary",
      status: null, // exception
      structure_percent: 0,
      files_percent: 0,
      msg: [],
      mod: false,
    };
  },
  beforeMount() {
    const vm = this;
    vm.repository = vm.$store.state.repository;
    vm.setting = vm.$store.state.setting;

    function parseData(data) {
      let result;
      switch (data?.type) {
        case "msg":
          result =
            vm.$i18n.t("all.info") +
            ": " +
            vm.$i18n.t(`websocket.${data?.msg}`);
          break;
        case "warn":
          result =
            vm.$i18n.t("all.warning") +
            ": " +
            vm.$i18n.t(`websocket.${data?.msg}`);
          if (data?.file !== undefined) result += ", " + data?.file;
          break;
        default:
          result = JSON.stringify(data);
          break;
      }
      return result;
    }

    // Websocket
    vm.websocket = new ArtonWebsocket();
    vm.websocket.onMessage = (message) => {
      if (message.data) {
        const msg = JSON.parse(message.data);
        const data = msg?.data;
        switch (msg?.type) {
          case "init":
            break;
          case "import":
            if (msg?.status != "fail") {
              switch (data?.type) {
                case "dir":
                  console.log(`structure progress ${data?.now}`);
                  break;
                case "msg":
                  switch (data?.msg) {
                    case "structure_done":
                      vm.structure_percent = 100.0;
                      break;
                    case "import_done":
                      vm.btn1_disabled = false;
                      vm.btn1_icon = "check-circle";
                      vm.btn1_loading = false;
                      vm.structure_percent = 100.0;
                      vm.files_percent = 100.0;
                      break;
                  }
                  vm.addMsg(parseData(data));
                  break;
                case "files_progress":
                  const percent = (100.0 * data.now) / data.total;
                  vm.files_percent = new Number(percent.toFixed(2));
                  vm.btn1_loading = true;
                  vm.structure_percent = 100.0;
                  break;
                default:
                  vm.addMsg(parseData(data));
                  break;
              }
            } else {
              vm.addMsg(`Failed, error=${msg?.err}, ${parseData(data)}`);
            }
            break;
          default:
            vm.addMsg(message.data);
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

    if (!vm.repository.wid) {
      return;
    }

    // Websocket onnect
    vm.websocket.connect(`ws://${vm.setting.address}/dir`);
  },

  beforeDestroy() {
    this.websocket.close();
  },

  props: ["current", "visible"],

  methods: {
    addMsg(data) {
      const vm = this;
      if (vm.msg.length > 100) {
        vm.msg.splice(0, 1);
      }
      vm.msg.push(data);
    },
    init(target) {
      const vm = this;
      vm.mod = false;
    },
    afterVisibleChange(val) {},
    onClose() {
      const vm = this;
      vm.$emit("on-close", vm.mod);
      vm.msg.splice(0, vm.msg.length);
      vm.path = "";
    },
    btn1Click(e) {
      const vm = this;
      vm.mod = true;
      vm.btn1_icon = "";
      vm.btn1_loading = true;
      vm.btn1_type = "primary";
      vm.structure_percent = 0;
      vm.files_percent = 0;
      vm.msg.splice(0, vm.msg.length);

      // Sending request
      const body = {
        wid: vm.repository.wid,
        path: vm.path,
        current: vm.current,
        delete: vm.setting.delete,
        encrypt: vm.setting.encrypt,
      };
      const onError = () => {
        console.log(`[Error] failed to import dir ${body.path}`);
        vm.btn1_disabled = false;
        vm.btn1_icon = "exclamation-circle";
        vm.btn1_loading = false;
        vm.btn1_type = "danger";
      };
      vm.$http
        .post(`http://${vm.setting.address}/dir/import`, body, options)
        .then(
          (resp) => {
            vm.btn1_loading = false;
            if (resp.body.status === "success") {
              vm.btn1_disabled = false;
              vm.btn1_icon = "check-circle";
              vm.files_percent = 100.0;
            } else {
              onError();
            }
          },
          (error) => {
            onError();
          }
        );
    },
  },
};
</script>

<style>
.ant-drawer > .ant-drawer-content-wrapper {
  min-width: 500px;
}

.tooltip-structure {
  margin-right: 10px;
}

.logging-wrapper {
  min-height: 50px;
  max-height: calc(100vh - 500px);
  overflow: auto;
}

#btn-wrapper {
  position: absolute;
  left: 50%;
  bottom: 6px;
  transform: translate(-50%, -50%);
}
</style>