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

    <div class="toolbar">
      <!-- Left buttons -->
      <div class="toolbar-left">
        <a-button
          class="tool-button"
          icon="cloud-upload"
          type="primary"
          @click="btn1Click"
          >{{ $t("all.import") }}</a-button
        >

        <!-- Upload -->
        <a-button class="tool-button" icon="folder-add" @click="mkdir">{{
          $t("all.mkdir")
        }}</a-button>
      </div>

      <!-- Right buttons -->
      <div class="toolbar-right">
        <transition name="slide-fade">
          <a-button
            v-if="button2_visible"
            class="tool-button-right"
            icon="delete"
            type="danger"
            :disabled="!button2_visible"
            @click="btn2Click"
            >{{ $t("all.delete") }}</a-button
          >
        </transition>
      </div>
    </div>

    <!-- Dir selector -->
    <DirSelector ref="dirSelector" @ok="dirSelectorOK" />

    <div class="file-container">
      <div class="secondary-menu">
        <!-- Breadcrumb -->
        <a-breadcrumb :routes="breadcrumb">
          <a-breadcrumb-item href></a-breadcrumb-item>
          <template slot="itemRender" slot-scope="{ route }">
            <a-icon v-if="route.icon != null" :type="route.icon" />&nbsp;
            <a @click="goto(route, $event)">{{ route.label }}</a>
          </template>
        </a-breadcrumb>

        <!-- Switch view -->
        <a class="secondary-menu-right" @click="switchFileView">
          <a-icon
            v-if="file_view == 'grid'"
            type="unordered-list"
            :style="{ fontSize: '16px' }"
          />
          <a-icon
            v-else-if="file_view == 'list'"
            type="appstore"
            :style="{ fontSize: '16px' }"
          />
        </a>
      </div>

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
      />
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
      />

      <!-- Pagination -->
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
</template>

<script>
import { Modal } from "ant-design-vue";
import options from "@/config/request";

const data = [];
const breadcrumb_home = {
  id: 0,
  type: "breadcrumb",
  icon: "home",
  label: "home",
  breadcrumbName: "home",
  children: [],
  page_no: 1,
};

export default {
  data() {
    return {
      drawer1_visible: false,
      drawer2_visible: false,
      button2_visible: false,
      explorer: null,
      repository: null,
      setting: null,
      data,
      current: 0,
      breadcrumb_flat: null,
      breadcrumb: null,
      file_view: null,
      checked: null,
      page_no: 1,
      page_size: 15,
      total: 0,
    };
  },
  components: {
    DirSelector: () => import("@/components/DirSelector.vue"),
    InputBox: () => import("@/components/InputBox.vue"),
    ImportDrawer: () => import("./ImportDrawer"),
    TagDrawer: () => import("./TagDrawer"),
    FileGrid: () => import("./FileGrid"),
    FileList: () => import("./FileList"),
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
    let nocache = vm.explorer.nocache;
    if (nocache === undefined) {
      nocache = {
        current: 0,
        breadcrumb_flat: [breadcrumb_home],
        breadcrumb: [breadcrumb_home],
        file_view: "grid",
      };
      vm.$store.commit("updateExplorerNocache", nocache);
    }
    vm.current = nocache.current;
    vm.breadcrumb_flat = nocache.breadcrumb_flat;
    vm.breadcrumb = nocache.breadcrumb;
    vm.file_view = nocache.file_view;
  },
  mounted() {
    this.list();
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
      vm.button2_visible = false;
      vm.$refs.fileGrid?.clearCheck();
      vm.$refs.fileList?.clearCheck();
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
              onError();
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
    page1Change(page, pageSize) {
      const vm = this;
      vm.page_no = page;
      vm.page_size = pageSize;
      vm.breadcrumb_flat[vm.breadcrumb_flat.length - 1].page_no = page;
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
                onError();
              }
            );
        }
      );
    },
    switchFileView(e) {
      const vm = this;

      // on view switch
      vm.button2_visible = false;
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
    getThumb(i, obj) {
      const vm = this;

      // Sending request
      const body = {
        responseType: 'blob',
      };
      const onError = () => {
        // console.log(`[Error] failed to get thumb ${obj?.fullname}`);
      };
      vm.$http
        .get(`http://${vm.setting.address}${obj.thumb}`, body, options)
        .then(
          (resp) => {
            var reader = new FileReader();
            reader.onload = (e) => {
              obj.thumb_done = true;
              obj.thumb_loading = false;
              obj.thumb = e.target.result;
              vm.data.splice(i, 1, obj);
            };
            reader.readAsDataURL(resp.body);
          },
          (error) => {
            onError(error);
          }
        );
    },
    list() {
      const vm = this;

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
                    obj.thumb_loading = true;
                    vm.getThumb(obj_ord, obj);
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
            onError();
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
            onError();
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
        vm.button2_visible = true;
      } else {
        vm.button2_visible = false;
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
                        {`${vm.$i18n.t(
                          "menu.dropdown_menu.label1_caption"
                        )}: ${item.id}`}
                      </p>
                      <p>
                        {`${vm.$i18n.t(
                          "menu.dropdown_menu.label2_caption"
                        )}: ${size} (${data.size})`}
                      </p>
                    </div>
                  ) : (
                    <div>
                      <p>
                        {`${vm.$i18n.t(
                          "menu.dropdown_menu.label1_caption"
                        )}: ${item.id}`}
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
            onError();
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
        window.open(`http://${vm.setting.address}/media/link?wid=${vm.repository.wid}&attribute=${target.attribute}&filename=${target.fullname}`);
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
                  onError();
                }
              );
          }
        );
      } else {
        console.log(`[Error] unknown type ${target.type}`);
      }
    },
    goto(target, event) {
      const vm = this;
      if (target === undefined || target.id === undefined) return;

      vm.clear();

      let obj = null;
      for (let i in vm.data) {
        if (vm.data[i].id == target.id) {
          obj = vm.data[i];
          break;
        }
      }
      if (target.type == "breadcrumb" || target.type == "dir") {
        // update flat breadcrumb
        if (target.id === 0) {
          vm.breadcrumb_flat = [breadcrumb_home];
        } else {
          let breadcrumb_target = null;
          for (let i in vm.breadcrumb_flat) {
            vm.breadcrumb_flat[i].children = [];
            if (vm.breadcrumb_flat[i].id === target.id) {
              breadcrumb_target = parseInt(i) + 1;
            }
          }
          if (breadcrumb_target) {
            vm.breadcrumb_flat.splice(
              breadcrumb_target,
              vm.breadcrumb_flat.length - breadcrumb_target
            );
          } else {
            vm.breadcrumb_flat.push({
              id: obj.id,
              type: "breadcrumb",
              label: obj.name,
              breadcrumbName: obj.name + obj.id,
              page_no: 1,
            });
          }
        }

        // update current
        vm.current = target.id;
        vm.page_no = target.page_no ?? 1;

        // refresh list
        vm.list();

        // update breadcrumb
        vm.breadcrumb.splice(0, vm.breadcrumb.length);
        if (vm.breadcrumb_flat.length > vm.explorer.breadcrumb_max_len) {
          const fold_end =
            vm.breadcrumb_flat.length - vm.explorer.breadcrumb_max_len;
          for (let i = 1; i < fold_end; i++) {
            vm.breadcrumb_flat[0].children.push(vm.breadcrumb_flat[i]);
          }
          vm.breadcrumb.push(vm.breadcrumb_flat[0]);
          for (let i = fold_end; i < vm.breadcrumb_flat.length; i++) {
            vm.breadcrumb.push(vm.breadcrumb_flat[i]);
          }
        } else {
          for (let i in vm.breadcrumb_flat) {
            vm.breadcrumb.push(vm.breadcrumb_flat[i]);
          }
        }

        // update vuex
        vm.$store.commit("updateExplorerNocache", {
          current: vm.current,
          breadcrumb_flat: vm.breadcrumb_flat,
          breadcrumb: vm.breadcrumb,
        });
      } else if (target.type == "file") {
        // open tag drawer
        vm.addTag(target);
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
.file-container {
  margin-top: 8px;
}

.secondary-menu {
  display: flex;
  flex-direction: row;
  justify-content: space-between;
}

.file-toolbox {
  margin-top: 8px;
}

.file-pagination {
  position: absolute;
  left: 50%;
  bottom: 5px;
  transform: translate(-50%, 0%);
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