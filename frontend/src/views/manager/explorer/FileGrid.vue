<template>
  <div class="file-grid">
    <!-- File viewer menu -->
    <div class="file-grid-toolbar">
      <a-checkbox
        :indeterminate="indeterminate"
        :checked="checkAll"
        @change="onCheckAllChange"
        >{{ $t("all.select_all") }}
      </a-checkbox>
      <slot name="file-toolbar"></slot>
    </div>

    <a-checkbox-group :value="checkedList">
      <div class="file-grid-flex">
        <!-- Card -->
        <a-card
          class="file-card"
          v-for="item in data"
          :alt="item.fullname"
          :class='{"file-selected": selected == item.id}'
          :hoverable="true"
          :key="`${item.type}-${item.id}`"
          @dblclick="goto(item, $event)"
        >
          <a-checkbox
            slot="title"
            :value="`${item.type}-${item.id}`"
            @change="checkChange"
          >
            <a-tooltip
              v-if="item.fullname != item.title"
              :title="item.fullname"
              >{{ item.title }}</a-tooltip
            >
            <span v-else>{{ item.title }}</span>
          </a-checkbox>

          <!-- Main dropdown menu -->
          <DropdownMenu
            :trigger="['contextmenu']"
            :item="item"
            @add-tag="addTag"
            @del="del"
            @detail="detail"
            @download="download"
            @goto="goto"
            @moveto="moveto"
            @rename="rename"
          >
            <!-- Image -->
            <div>
              <img
                v-show="item.thumb_done"
                class="grid-thumb"
                :key="`${item.fullname}${Math.random()}`"
                :alt="item.fullname"
                :src="item.thumb"
                @load="onLoad(item)"
              />
              <img
                v-if="!item.thumb_done"
                class="grid-icon"
                :alt="item.fullname"
                :src="item.icon"
              />
            </div>
          </DropdownMenu>

          <!-- Secondary dropdown menu -->
          <DropdownMenu
            slot="extra"
            :trigger="['click']"
            :item="item"
            @add-tag="addTag"
            @del="del"
            @detail="detail"
            @download="download"
            @goto="goto"
            @moveto="moveto"
            @rename="rename"
          >
            <a-icon type="down-circle" />
          </DropdownMenu>
        </a-card>
      </div>
    </a-checkbox-group>
  </div>
</template>

<script>
const defaultCheckedList = [];

export default {
  data() {
    return {
      checkAll: false,
      checkedList: defaultCheckedList,
      indeterminate: false,
      lastShiftValue: undefined,
    };
  },
  beforeMount() {
    const vm = this;
  },
  components: {
    DropdownMenu: () => import("@/components/DropdownMenu.vue"),
  },
  computed: {},
  props: ["data", "selected"],
  methods: {
    addTag(target, event) {
      this.$emit("add-tag", target, event);
    },
    del(target, event) {
      this.$emit("del", target, event);
    },
    detail(target, event) {
      this.$emit("detail", target, event);
    },
    download(target, event) {
      this.$emit("download", target, event);
    },
    goto(target, event) {
      this.$emit("goto", target, event);
    },
    moveto(target, event) {
      this.$emit("moveto", target, event);
    },
    rename(target, event) {
      this.$emit("rename", target, event);
    },
    clearCheck() {
      const vm = this;
      vm.checkedList.splice(0, vm.checkedList.length);
      Object.assign(vm, {
        indeterminate: false,
        checkAll: false,
      });
    },
    onCheckAllChange(e) {
      const vm = this;
      vm.checkedList.splice(0, vm.checkedList.length);
      if (e.target.checked) {
        for (let i in vm.data) {
          vm.checkedList.push(`${vm.data[i].type}-${vm.data[i].id}`);
        }
      }
      Object.assign(vm, {
        indeterminate: false,
        checkAll: e.target.checked,
      });

      // emit
      vm.$emit("check", vm.checkedList, e);
    },
    onLoad(item) {
      item.thumb_done = true;
    },
    checkChange(e) {
      const vm = this;
      const checkedSet = new Set(vm.checkedList);

      // deal with shift
      if (e.nativeEvent.shiftKey) {
        if (vm.lastShiftValue === undefined) {
          vm.lastShiftValue = e.target.value;
        } else {
          // add all selected
          const start = Math.min(e.target.value, vm.lastShiftValue);
          const end = Math.max(e.target.value, vm.lastShiftValue);
          for (let i = start; i <= end; i++) {
            if (e.target.checked) {
              checkedSet.add(i.toString());
            } else {
              checkedSet.delete(i.toString());
            }
          }
        }
      } else {
        vm.lastShiftValue = undefined; // clear shift value
      }
      if (e.target.checked) {
        checkedSet.add(e.target.value.toString());
      } else {
        checkedSet.delete(e.target.value.toString());

        vm.lastShiftValue = undefined; // clear shift value
      }

      // update status
      vm.checkedList.splice(0, vm.checkedList.length);
      checkedSet.forEach((value) => {
        vm.checkedList.push(value);
      });
      const length = vm.checkedList.length;
      Object.assign(vm, {
        indeterminate: 0 < length && length < vm.data.length,
        checkAll: length === vm.data.length,
      });

      // emit
      vm.$emit("check", vm.checkedList, e);
    },
  },
};
</script>


<style>
.ant-card-head {
  min-height: 30px;
  height: 30px;
  padding: 0 12px;
}

.ant-card-head-wrapper {
  height: 30px;
}

.ant-card-head-title {
  padding: 4px 0;
}

.ant-card-hoverable {
  cursor: auto;
  border-radius: 5px;
}

.ant-card-hoverable:hover {
  border: 1px solid #80cef8;
  background-color: #e1eaf5;
}

.ant-card-hoverable:hover .ant-card-head {
  border-bottom-color: #80cef8;
}

.ant-checkbox-group {
  display: block;
  height: 100%;
}

.file-card {
  margin: 0 0 10px 10px;
  max-height: 150px;
  width: 150px;
}

.file-card > .ant-card-body {
  height: 110px;
  text-align: center;
  padding: 5px;
}

.file-grid {
  height: 100%;
}

.file-grid-flex {
  height: calc(100% - 24px);
  overflow: auto;
  display: flex;
  flex-flow: row wrap;
  justify-content: flex-start;
}

.file-grid-toolbar {
  margin-bottom: 3px;
}

.grid-icon {
  width: 100%;
  max-height: 100px;
  max-width: 100px;
}

.grid-thumb {
  max-height: 100px;
  max-width: 140px;
}
</style>