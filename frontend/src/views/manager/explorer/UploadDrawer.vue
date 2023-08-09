<template>
  <a-drawer
    id="upload-drawer"
    placement="right"
    width="50vw"
    :closable="true"
    :maskClosable="true"
    :title="$t('explorer.upload_drawer.title')"
    :visible="visible"
    :after-visible-change="afterVisibleChange"
    @close="onClose"
  >
    <a-upload-dragger
      class="upload-dragger"
      name="file"
      :multiple="true"
      :showUploadList="false"
      :before-upload="beforeUpload"
      @change="handleChange"
    >
      <ul class="upload-wrapper">
        <li><a-icon type="inbox" /></li>
        <li>
          {{ $t("explorer.upload_drawer.upload_text") }}
          <br />
          {{ $t("explorer.upload_drawer.upload_hint") }}
        </li>
      </ul>
    </a-upload-dragger>

    <!-- File list -->
    <a-divider />
    <b>
      {{
        $t("explorer.upload_drawer.label1_caption") +
        `(${file_count_dup}/${file_count})`
      }}
    </b>
    <div class="filelist-wrapper">
      <a-table
        rowKey="fullname"
        :columns="columns"
        :data-source="fileList"
        :pagination="pagination"
      >
        <span slot="name" slot-scope="item">
          <a-tooltip :title="item.fullname">
            {{ item.name }}
          </a-tooltip>
        </span>

        <span slot="dup" slot-scope="item">
          <a-icon v-if="item.dup == 'no_attr'" type="file-add" />
          <a-tooltip v-else :title="item.dup">
            {{ item.dupname }}
          </a-tooltip>
        </span>

        <span slot="action" slot-scope="item">
          <a-icon
            v-if="item.state == 'done'"
            type="check-circle"
            theme="twoTone"
            two-tone-color="#52c41a"
          />
          <a-icon
            v-else-if="item.state == 'err'"
            type="close-circle"
            theme="twoTone"
            two-tone-color="#eb2f96"
          />
          <a v-else @click="handleRemove(item)"><a-icon type="delete" /></a>
        </span>
      </a-table>
    </div>

    <a-row id="btn-wrapper">
      <a-col :span="2"> </a-col>
      <a-col :span="20">
        <a-button @click="btn2Click" class="tool-button">
          {{ $t("all.clear") }}
        </a-button>
        <a-button class="tool-button" @click="btn3Click">
          {{ $t("explorer.upload_drawer.btn3_caption") }}
        </a-button>
        <a-button
          class="tool-button"
          :disabled="btn1_disabled"
          :icon="btn1_icon"
          :loading="btn1_loading"
          :type="btn1_type"
          @click="btn1Click"
        >
          {{ $t("all.import") }}
        </a-button>
      </a-col>
      <a-col :span="2"> </a-col>
    </a-row>
  </a-drawer>
</template>

<script>
import options from "@/config/request";

export default {
  data() {
    return {
      btn1_disabled: true,
      btn1_icon: "",
      btn1_loading: false,
      btn1_type: "primary",
      columns: [],
      fileList: [],
      file_count: 0,
      file_count_dup: 0,
      mod: false,
      pagination: {
        pageSize: 8,
        position: "top",
        size: "small",
      },
      repository: null,
      setting: null,
    };
  },
  beforeMount() {
    const vm = this;
    vm.repository = vm.$store.state.repository;
    vm.setting = vm.$store.state.setting;

    if (!vm.repository.wid) {
      return;
    }

    const columns = [
      {
        title: vm.$i18n.t("explorer.upload_drawer.table1.name"),
        key: "name",
        scopedSlots: { customRender: "name" },
      },
      {
        align: "left",
        title: vm.$i18n.t("explorer.upload_drawer.table1.dup"),
        key: "dup",
        scopedSlots: { customRender: "dup" },
      },
      {
        align: "center",
        title: vm.$i18n.t("explorer.upload_drawer.table1.action"),
        key: "action",
        scopedSlots: { customRender: "action" },
        width: 80,
      },
    ];
    columns.forEach((item) => {
      vm.columns.push(item);
    });
  },

  beforeDestroy() {},

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
    afterVisibleChange(visible) {},
    beforeUpload(file) {
      return false;
    },
    handleChange(info) {
      const vm = this;
      let name = info.file.name;
      if (name.length > 20) {
        name = `${name.slice(0, 20)}...`;
      }
      const fileInfo = {
        dup: "",
        dupname: "",
        file: info.file,
        name,
        fullname: info.file.name,
        state: "none",
      };
      vm.fileList = [...vm.fileList, fileInfo];
      vm.btn1_disabled = false;

      // Sending request
      const formData = new FormData();
      formData.append("wid", vm.repository.wid);
      formData.append("file", info.file);
      const onError = () => {
        console.log(`[Error] failed to check exist ${info.file.name}`);
      };
      vm.file_count = 0;
      vm.file_count_dup = 0;
      vm.$http
        .post(`http://${vm.setting.address}/file/exist`, formData, options)
        .then(
          (resp) => {
            if (resp.body.status === "success") {
              let dupname = resp.data.data;
              vm.file_count += 1;
              if (dupname != "no_attr") vm.file_count_dup += 1;
              if (dupname.length > 30) {
                dupname = `${dupname.slice(0, 50)}...`;
              }
              fileInfo.dup = resp.data.data;
              fileInfo.dupname = dupname;
            } else {
              onError();
            }
          },
          (error) => {
            onError();
          }
        );
    },
    handleRemove(item) {
      const vm = this;
      const index = vm.fileList.indexOf(item);
      vm.fileList.splice(index, 1);
      vm.btn1_disabled = vm.fileList.length <= 0;
    },
    onClose() {
      const vm = this;
      vm.$emit("on-close", vm.mod);
    },
    async btn1Click(e) {
      const vm = this;
      for (const i in vm.fileList) {
        await this.upload(vm.fileList[i]);
      }
    },
    btn2Click() {
      const vm = this;
      vm.file_count = 0;
      vm.file_count_dup = 0;
      vm.fileList.splice(0, vm.fileList.length);
      vm.btn1_disabled = true;
    },
    btn3Click() {
      const vm = this;
      vm.file_count_dup = 0;
      vm.fileList = vm.fileList
        .filter((item) => item.dup == "no_attr" && item.state != "done")
        .sort((a, b) => a.fullname.localeCompare(b.fullname));
      vm.file_count = vm.fileList.length;
      vm.btn1_disabled = vm.fileList.length <= 0;
    },
    upload(info) {
      const vm = this;
      vm.btn1_disabled = true;

      // Sending request
      const formData = new FormData();
      formData.append("wid", vm.repository.wid);
      formData.append("current", vm.current);
      formData.append("encrypt", vm.setting.encrypt);
      formData.append("file", info.file);
      const onError = (e) => {
        console.log(`[Error] failed to upload ${info.file.name}, err=${e}`);
        vm.btn1_disabled = false;
        info.state = "err";
      };
      return vm.$http
        .post(`http://${vm.setting.address}/file/upload`, formData, options)
        .then(
          (resp) => {
            if (
              resp.body.status === "success" &&
              resp.data.status === "success"
            ) {
              info.state = "done";
              vm.mod = true; // Add mod flag
            } else {
              onError(resp.data?.err);
            }
          },
          (error) => {
            onError(error);
          }
        );
    },
  },
};
</script>

<style>
#upload-drawer .ant-drawer-body {
  height: calc(100% - 35px);
}

#upload-drawer .ant-drawer-content-wrapper {
  min-width: 300px;
}

.upload-dragger .ant-upload.ant-upload-drag {
  height: 20%;
  min-height: 90px;
}

.upload-wrapper {
  display: inline-block;
  padding-left: 0;
}

.upload-wrapper::before {
  content: "";
  display: inline-block;
  height: 100%;
  position: relative;
  vertical-align: middle;
  width: 0;
}

.upload-wrapper .anticon {
  color: #40a9ff;
  font-size: 48px;
}

.upload-wrapper > li {
  display: inline-block;
  vertical-align: middle;
}

.tooltip-structure {
  margin-right: 10px;
}

.filelist-wrapper {
  min-height: 50px;
  height: calc(80% - 130px);
  overflow: auto;
}

.filelist-wrapper .ant-table-wrapper {
  height: 100%;
}

#btn-wrapper {
  bottom: 6px;
  text-align: center;
  width: 100%;
}
</style>

<style scoped>
#btn-wrapper {
  position: absolute;
  left: 50%;
  bottom: 6px;
  transform: translate(-50%, -50%);
}
</style>