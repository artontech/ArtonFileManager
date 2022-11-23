<template>
  <div class="explorer">
    <!-- Components -->
    <InputBox ref="inputBox" />
    <ImportDrawer
      ref="importDrawer"
      :current="current"
      :visible="drawer1_visible"
      @on-close="drawer1Close"
    />
    <TagDrawer
      ref="tagDrawer"
      :visible="drawer2_visible"
      @on-close="drawer2Close"
    />
    <UploadDrawer
      ref="uploadDrawer"
      :current="current"
      :visible="drawer3_visible"
      @on-close="drawer3Close"
    />

    <div class="toolbar">
      <!-- Left buttons -->
      <div class="toolbar-left">
        <a-button
          class="tool-button"
          icon="cloud-upload"
          size="small"
          type="primary"
          @click="btn1Click"
        >
          {{ $t("all.import") }}
        </a-button>

        <!-- Upload -->
        <a-button
          class="tool-button"
          icon="upload"
          size="small"
          type="primary"
          @click="btn4Click"
        >
          {{ $t("all.upload") }}
        </a-button>

        <a-button
          class="tool-button"
          icon="folder-add"
          size="small"
          @click="mkdir"
        >
          {{$t("all.mkdir")}}
        </a-button>
      </div>

      <!-- Right buttons -->
      <div class="toolbar-right">
        <transition name="slide-fade">
          <div v-if="tool_button_visible">
            <a-button
              class="tool-button-right"
              icon="download"
              size="small"
              type="primary"
              :loading="btn1_loading"
              @click="btn3Click"
              >{{ $t("all.export") }}
            </a-button>
            <a-button
              class="tool-button-right"
              icon="delete"
              size="small"
              type="danger"
              :disabled="!tool_button_visible"
              @click="btn2Click"
              >{{ $t("all.delete") }}</a-button
            >
          </div>
        </transition>
      </div>
    </div>

    <!-- Dir selector -->
    <DirSelector ref="dirSelector" @ok="dirSelectorOK" />

    <div class="file-container">
      <!-- File viewer -->
      <FileGrid
        ref="fileGrid"
        v-if="file_view == 'grid'"
        :data="data"
        @add-tag="addTag"
        @check="check"
        @del="del"
        @detail="detail"
        @download="download"
        @goto="goto"
        @moveto="moveto"
        @rename="rename"
      >
        <FileToolbar
          slot="file-toolbar"
          :current_dir="current_dir"
          :file_view="file_view"
          @goto="goto"
          @switch-file-view="switchFileView"
        />
      </FileGrid>
      <FileList
        ref="fileList"
        v-else-if="file_view == 'list'"
        :data="data"
        @add-tag="addTag"
        @check="check"
        @del="del"
        @detail="detail"
        @download="download"
        @goto="goto"
        @moveto="moveto"
        @rename="rename"
      >
        <FileToolbar
          slot="file-toolbar"
          :current_dir="current_dir"
          :file_view="file_view"
          @goto="goto"
          @switch-file-view="switchFileView"
        />
      </FileList>

      <!-- Pagination -->
      <div class="file-pagination-wrapper">
        <a-pagination
          class="file-pagination"
          size="small"
          show-quick-jumper
          show-size-changer
          :hideOnSinglePage="false"
          :current="page_no"
          :pageSize="page_size"
          :pageSizeOptions="['5', '15', '30', '60']"
          :total="total"
          :show-total="(total) => `Total ${total}`"
          @change="page1Change"
          @showSizeChange="page1Change"
        />
      </div>
    </div>
  </div>
</template>

<script>
import { Modal } from "ant-design-vue";
import options from "@/config/request";
import { http_post } from "@/util/HttpRequest";

const data = [];

export default {
  data() {
    return {
      drawer1_visible: false,
      drawer2_visible: false,
      drawer3_visible: false,
      tool_button_visible: false,
      btn1_loading: false,
      explorer: null,
      repository: null,
      setting: null,
      data,
      current: 0,
      dir_info: null,
      file_view: null,
      checked: null,
      page_no: 1,
      page_size: 15,
      current_dir: {id: 0, name: "/"},
      total: 0,
    };
  },
  components: {
    DirSelector: () => import("@/components/DirSelector.vue"),
    InputBox: () => import("@/components/InputBox.vue"),
    ImportDrawer: () => import("./ImportDrawer"),
    TagDrawer: () => import("./TagDrawer"),
    UploadDrawer: () => import("./UploadDrawer"),
    FileGrid: () => import("./FileGrid"),
    FileList: () => import("./FileList"),
    FileToolbar: () => import("@/components/FileToolbar"),
  },
  beforeMount() {
    const vm = this;
    vm.explorer = vm.$store.state.explorer;
    vm.repository = vm.$store.state.repository;
    vm.setting = vm.$store.state.setting;

    if (!vm.repository.wid) {
      vm.$router.go("Repository");
      return;
    }

    // deal with nocache items
    let nocache = vm.explorer.nocache, need_update = false;
    if (nocache === undefined) {
      nocache = {
        current: 0,
        dir_info: {"0": {page: 1}},
        file_view: "grid",
      };
      need_update = true;
    }
    if (vm.$route.query.current !== undefined) {
      nocache.current = vm.$route.query.current;
      need_update = true;
    }
    vm.current = vm.$route.query.current ?? nocache.current;
    vm.dir_info = nocache.dir_info;
    vm.file_view = nocache.file_view;
    vm.newDirInfo();
    vm.page_no = vm.getDirInfo().page;
    if (need_update) {
      vm.$store.commit("updateExplorerNocache", nocache);
    }
  },
  mounted() {
    const vm = this;
    vm.getDir(vm.current).then((dir) => {
      vm.current_dir = dir;
    });
    vm.list();
  },
  computed: {},
  methods: {
    formatSize(size) {
      let appendix = "Byte";
      if (size > 1024) {
        size /= 1024.0;
        appendix = "KB";
      }
      if (size > 1024) {
        size /= 1024.0;
        appendix = "MB";
      }
      if (size > 1024) {
        size /= 1024.0;
        appendix = "GB";
      }
      return `${new Number(size.toFixed(2))} ${appendix}`;
    },
    clear() {
      const vm = this;

      // disable delete button & clear check
      vm.tool_button_visible = false;
      vm.$refs.fileGrid?.clearCheck();
      vm.$refs.fileList?.clearCheck();
    },
    getDirInfo() {
      const vm = this;
      return vm.dir_info[`${vm.current}`];
    },
    getDir(id) {
      const vm = this;

      const body = {
        wid: vm.repository.wid,
        target: id,
      };
      return vm.http_post(`http://${vm.setting.address}/dir/getdir`, body);
    },
    http_post(url, body) {
      return http_post(this, url, body);
    },
    newDirInfo() {
      const vm = this;
      if (!vm.dir_info[`${vm.current}`]) {
        vm.dir_info[`${vm.current}`] = {page: 1};
      }
    },

    /* * * * * * * * Start: Trigger * * * * * * * */
    btn1Click(event) {
      const vm = this;
      vm.$refs.importDrawer.init();
      vm.drawer1_visible = true;
    },
    btn2Click(event) {
      const vm = this;
      let types = [],
        ids = [];

      vm.checked.forEach((s) => {
        let sp = s.split("-");
        types.push(sp[0]);
        ids.push(sp[1]);
      });
      vm.update(types.toString(), ids.toString(), null, null, 1, () => {
        vm.clear();
      });
    },
    btn3Click(event) {
      const vm = this;
      let targets = [];
      vm.btn1_loading = true;
      vm.checked.forEach((s) => {
        let sp = s.split("-");
        if (sp[0] != "file") {
          // TODO: Export dir
          return;
        }
        for (let i = 0; i < vm.data.length; i++) {
          const target = vm.data[i];
          if (target.id == sp[1]) {
            targets.push({
              attribute: target.attribute,
              ext: target.ext,
              id: target.id,
              type: target.type,
              name: target.name,
            });
            break;
          }
        }
      });

      // Sending request
      const onError = () => {
        console.log(`[Error] failed to export`, targets);
        vm.btn1_loading = false;
        vm.$message.error(vm.$i18n.t("explorer.export_fail"));
      };
      const body = {
        wid: vm.repository.wid,
        targets,
        export_path: vm.setting.exportpath,
      };
      vm.$http
        .post(`http://${vm.setting.address}/media/export`, body, options)
        .then(
          (resp) => {
            const data = resp.body?.data;
            if (data && resp.body?.status === "success") {
              vm.btn1_loading = false;
              vm.$message.success(vm.$i18n.t("explorer.export_done"));
            } else {
              onError();
            }
          },
          (error) => {
            onError(error);
          }
        );
    },
    btn4Click(event) {
      const vm = this;
      vm.$refs.uploadDrawer.init();
      vm.drawer3_visible = true;
    },
    dirSelectorOK(mode, target, selected_keys) {
      const vm = this;
      if (!target) return;

      if ("moveto" == mode) {
        // Sending request
        const body = {
          wid: vm.repository.wid,
          type: target.type,
          from: Number(target.id),
          to: Number(selected_keys[0]),
        };
        const onError = () => {
          console.log(
            `[Error] failed to move target ${target} to ${selected_keys[0]}`
          );
        };
        vm.$http
          .post(`http://${vm.setting.address}/dir/moveto`, body, options)
          .then(
            (resp) => {
              if (resp.body.status === "success") {
                vm.clear();
                vm.list();
              } else {
                onError();
              }
            },
            (error) => {
              onError(error);
            }
          );
      }
    },
    drawer1Close(mod) {
      const vm = this;
      vm.drawer1_visible = false;
      if (mod) vm.list();
    },
    drawer2Close(mod) {
      const vm = this;
      vm.drawer2_visible = false;
      if (mod) vm.list();
    },
    drawer3Close(mod) {
      const vm = this;
      vm.drawer3_visible = false;
      if (mod) vm.list();
    },
    page1Change(page, pageSize) {
      const vm = this;
      vm.page_no = page;
      vm.page_size = pageSize;
      vm.getDirInfo().page = page;
      vm.list();
    },
    mkdir() {
      const vm = this;
      vm.$refs.inputBox.initShow(
        vm.$i18n.t("explorer.dir_input.title"),
        vm.$i18n.t("explorer.dir_input.placeholder"),
        null,
        (value) => {
          // Sending request
          const body = {
            wid: vm.repository.wid,
            current: vm.current,
            name: value,
          };
          const onError = () => {
            console.log(`[Error] failed to create dir ${value}`);
          };
          vm.$http
            .post(`http://${vm.setting.address}/dir/create`, body, options)
            .then(
              (resp) => {
                if (resp.body.status === "success") {
                  vm.list();
                } else {
                  onError();
                }
              },
              (error) => {
                onError(error);
              }
            );
        }
      );
    },
    switchFileView(e) {
      const vm = this;

      // on view switch
      vm.tool_button_visible = false;
      if (vm.file_view == "grid") {
        vm.$refs.fileGrid.clearCheck();
        vm.file_view = "list";
      } else {
        vm.$refs.fileList.clearCheck();
        vm.file_view = "grid";
      }

      // update vuex
      vm.$store.commit("updateExplorerNocache", {
        file_view: vm.file_view,
      });
    },
    /* * * * * * * * End: Trigger * * * * * * * */

    /* * * * * * * * Start: File viewer * * * * * * * */
    list() {
      const vm = this;

      // update vuex
      vm.newDirInfo();
      vm.$store.commit("updateExplorerNocache", {
        current: vm.current,
        dir_info: vm.dir_info,
      });

      if (!vm.repository.wid) {
        return;
      }

      // Sending request
      const body = {
        wid: vm.repository.wid,
        current: vm.current,
        thumb: vm.setting.showthumb,
        dir: true,
        file: true,
        page_no: vm.page_no,
        page_size: vm.page_size,
      };
      const onError = () => {
        console.log(`[Error] failed to list dir ${body.current}`);
      };
      vm.$http
        .post(`http://${vm.setting.address}/dir/list`, body, options)
        .then(
          (resp) => {
            const data = resp.body?.data;
            if (data && resp.body?.status === "success") {
              vm.data.splice(0, vm.data.length);
              data.list?.forEach((obj) => {
                if (obj.delete) return;
                obj.icon = `http://${vm.setting.address}${obj.icon}`;

                // Add more attr
                obj.key = obj.id;

                if (obj.type == "dir") {
                  obj.fullname = obj.name;
                } else if (obj.type == "file") {
                  obj.fullname = obj.name + obj.ext;

                  // fetch thumb
                  const obj_ord = vm.data.length;
                  if (obj.thumb) {
                    obj.thumb = `http://${vm.setting.address}` +
                      `${obj.thumb}&filename=thumb&cache=${vm.setting.cachethumb}`;
                  }
                } else {
                  console.log("[Error] unknown type", obj);
                }

                if (obj.fullname?.length > 6) {
                  obj.title = `${obj.fullname.slice(0, 6)}...`;
                } else {
                  obj.title = obj.fullname;
                }
                obj.thumb_done = false;
                vm.data.push(obj);
              });

              vm.total = data.total ? data.total : 0;
            } else {
              onError();
            }
          },
          (error) => {
            onError(error);
          }
        );
    },
    update(types, ids, name, ext, del, onSuccess) {
      const vm = this;

      // Sending request
      const body = {
        wid: vm.repository.wid,
        type: types,
        target: ids,
        name,
        ext,
        delete: del,
      };
      const onError = () => {
        console.log(`[Error] failed to delete ${ids}`);
      };
      vm.$http
        .post(`http://${vm.setting.address}/dir/update`, body, options)
        .then(
          (resp) => {
            if (resp.body.status === "success") {
              vm.list();
              if (onSuccess) onSuccess();
            } else {
              onError();
            }
          },
          (error) => {
            onError(error);
          }
        );
    },

    // Events
    addTag(target, e) {
      const vm = this;
      vm.$refs.tagDrawer.init(target);
      vm.drawer2_visible = true;
    },
    check(checked, e) {
      const vm = this;

      vm.checked = null;
      if (checked.length > 0) {
        vm.checked = checked;
        vm.tool_button_visible = true;
      } else {
        vm.tool_button_visible = false;
      }
    },
    del(target, e) {
      const vm = this;

      vm.update(target.type, target.id, null, null, 1, () => {
        vm.clear();
      });
    },
    detail(item, event) {
      const vm = this,
        target = item.type == "file" ? item.attribute : item.id;

      // Sending request
      const body = {
        wid: vm.repository.wid,
        target,
        type: item.type,
      };
      const onError = () => {
        console.log(`[Error] failed to get detail ${target}`);
      };
      vm.$http
        .post(`http://${vm.setting.address}/dir/detail`, body, options)
        .then(
          (resp) => {
            const data = resp.body?.data;
            if (data && resp.body?.status === "success") {
              const size = vm.formatSize(data.size);
              Modal.info({
                content:
                  item.type == "file" ? (
                    <div>
                      <p>
                        {`${vm.$i18n.t("menu.dropdown_menu.label1_caption")}: ${
                          item.id
                        }`}
                      </p>
                      <p>
                        {`${vm.$i18n.t(
                          "menu.dropdown_menu.label2_caption"
                        )}: ${size} (${data.size})`}
                      </p>
                      <p>
                        {`${vm.$i18n.t("all.attr_id")}: ${data.id}`}
                      </p>
                      <p>
                        {`${vm.$i18n.t("all.ahash")}: ${data.ahash}`}
                      </p>
                      <p>
                        {`${vm.$i18n.t("all.dhash")}: ${data.dhash}`}
                      </p>
                      <p>
                        {`${vm.$i18n.t("all.phash")}: ${data.phash}`}
                      </p>
                    </div>
                  ) : (
                    <div>
                      <p>
                        {`${vm.$i18n.t("menu.dropdown_menu.label1_caption")}: ${
                          item.id
                        }`}
                      </p>
                      <p>
                        {`${vm.$i18n.t(
                          "menu.dropdown_menu.label2_caption"
                        )}: ${size} (${data.size})`}
                      </p>
                      <p>
                        {`${vm.$i18n.t("menu.dropdown_menu.label3_caption")}: ${
                          data.file_count
                        }`}
                      </p>
                      <p>
                        {`${vm.$i18n.t("menu.dropdown_menu.label4_caption")}: ${
                          data.dir_count
                        }`}
                      </p>
                    </div>
                  ),
              });
            }
          },
          (error) => {
            onError(error);
          }
        );
    },
    download(target, event) {
      const vm = this;

      // Sending request
      const onError = () => {
        console.log(`[Error] failed to download ${target.fullname}`);
      };

      if (target.type == "file") {
        window.open(
          `http://${vm.setting.address}/media/link` +
          `?wid=${vm.repository.wid}&attribute=${target.attribute}` +
          `&filename=${encodeURIComponent(target.fullname)}&cache=${vm.setting.cachethumb}`
        );
      } else if (target.type == "dir") {
        vm.$refs.inputBox.initShow(
          vm.$i18n.t("explorer.export.title"),
          vm.$i18n.t("explorer.export.placeholder"),
          "D:\\tmp\\export",
          (value) => {
            const body = {
              wid: vm.repository.wid,
              current: target.id,
              name: target.name,
              path: value,
            };
            vm.$http
              .post(`http://${vm.setting.address}/dir/export`, body, options)
              .then(
                (resp) => {
                  const data = resp.body?.data;
                  if (data && resp.body?.status === "success") {
                    console.log("Export done");
                  } else {
                    onError();
                  }
                },
                (error) => {
                  onError(error);
                }
              );
          }
        );
      } else {
        console.log(`[Error] unknown type ${target.type}`);
      }
    },
    goto(target, event) {
      event;
      const vm = this;
      if (target === undefined || target.type === undefined) return;

      vm.clear();

      switch (target.type) {
        case "home":
          vm.current = 0;
          break;
        case "back":
          vm.current = vm.current_dir?.parent;
          break;
        case "dir":
          // update current
          vm.current = target.id;
          break;
        case "file":
          // open tag drawer
          vm.addTag(target);
          break;
      }
      
      switch (target.type) {
        case "home":
        case "back":
        case "dir":
          vm.$router.push({
            name: 'Explorer',
            query: {
              current: vm.current
            },
          });
          break;
        case "file":
          break;
      }
    },
    moveto(target, e) {
      const vm = this;
      vm.$refs.dirSelector.initShow("moveto", target);
    },
    rename(target, e) {
      const vm = this;

      vm.$refs.inputBox.initShow(
        vm.$i18n.t("explorer.rename.title"),
        vm.$i18n.t("explorer.rename.placeholder"),
        target.name,
        (value) => {
          vm.update(target.type, target.id, value, null, null, () => {
            vm.list();
          });
        }
      );
    },
    /* * * * * * * * End: File viewer * * * * * * * */
  },
};
</script>

<style>

.explorer {
  height: 100%;
}

.file-container {
  height: calc(100% - 56px);
  margin-top: 8px;
}

.file-pagination {
  display: inline-block;
  bottom: 5px;
}

.file-pagination-wrapper {
  height: 24px;
  width: 100%;
  text-align: center;
}

.ant-checkbox-group {
  width: 100%;
}

.ant-divider-horizontal {
  margin: 12px 0;
}

.icon {
  max-height: 80px;
}

.tool-button {
  margin-right: 10px;
}

.tool-button-right {
  margin-left: 10px;
}

.toolbar {
  display: flex;
  flex-direction: row;
  justify-content: space-between;
}

.slide-fade-enter-active {
  transition: all 0.3s ease;
}
.slide-fade-leave-active {
  transition: all 0.3s cubic-bezier(1, 0.5, 0.8, 1);
}
.slide-fade-enter,
.slide-fade-leave-to {
  transform: translateX(0px);
  opacity: 0;
}
</style>