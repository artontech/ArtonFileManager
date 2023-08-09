<template>
  <div class="search-file">
    <a-form
      class="ant-advanced-search-form"
      :form="form"
      @submit="handleSearch"
    >
      <a-row :gutter="24">
        <a-tabs v-model="mode" type="card" tab-position="top">
          <!-- Operation -->
          <a-row slot="tabBarExtraContent">
            <a-col :span="24" :style="{ textAlign: 'right' }">
              <a-button type="primary" html-type="submit" :loading="searching">
                {{ $t("search_file.btn1_caption") }}
              </a-button>
              <a-button :style="{ marginLeft: '8px' }" @click="handleReset">
                {{ $t("all.clear") }}
              </a-button>
            </a-col>
          </a-row>

          <a-tab-pane key="file" :tab="$t('search_file.tab1')">
            <!-- input name -->
            <a-col key="name" :span="16">
              <a-tooltip>
                <template slot="title">
                  {{ $t("search_file.prompt_name") }}
                </template>
                <a-form-item :label="$t('search_file.input_name_placeholder')">
                  <a-input
                    v-decorator="[
                      `name`,
                      // {initialValue: '%%',},
                    ]"
                    :placeholder="$t('search_file.input_name_placeholder')"
                  />
                </a-form-item>
              </a-tooltip>
            </a-col>

            <!-- input attr_id -->
            <a-col key="attr-id" :span="8">
              <a-form-item :label="$t('search_file.input4_placeholder')">
                <a-input-number
                  v-decorator="[
                    `attr_id`,
                    {
                      rules: [
                        {
                          required: false,
                          message: '!',
                        },
                      ],
                    },
                  ]"
                  :min="0"
                  :placeholder="$t('search_file.input4_placeholder')"
                />
              </a-form-item>
            </a-col>
          </a-tab-pane>
          <a-tab-pane key="dir" :tab="$t('search_file.tab2')">
            <!-- input name -->
            <a-col key="name" :span="16">
              <a-tooltip>
                <template slot="title">
                  {{ $t("search_file.prompt_name") }}
                </template>
                <a-form-item :label="$t('search_file.input_name_placeholder')">
                  <a-input
                    v-decorator="[`name`]"
                    :placeholder="$t('search_file.input_name_placeholder')"
                  />
                </a-form-item>
              </a-tooltip>
            </a-col>
          </a-tab-pane>
          <a-tab-pane key="hash" :tab="$t('search_file.tab3')">
            <!-- input ahash -->
            <a-col key="ahash" :span="8">
              <a-form-item :label="$t('search_file.input1_placeholder')">
                <a-input
                  v-decorator="[`ahash`]"
                  :placeholder="$t('search_file.input1_placeholder')"
                />
              </a-form-item>
            </a-col>

            <!-- input dhash -->
            <a-col key="dhash" :span="8">
              <a-form-item :label="$t('search_file.input2_placeholder')">
                <a-input
                  v-decorator="[`dhash`]"
                  :placeholder="$t('search_file.input2_placeholder')"
                />
              </a-form-item>
            </a-col>

            <!-- input phash -->
            <a-col key="phash" :span="8">
              <a-form-item :label="$t('search_file.input3_placeholder')">
                <a-input
                  v-decorator="[`phash`]"
                  :placeholder="$t('search_file.input3_placeholder')"
                />
              </a-form-item>
            </a-col>
          </a-tab-pane>
          <a-tab-pane key="face" :tab="$t('search_file.tab4')"> </a-tab-pane>
        </a-tabs>
      </a-row>
    </a-form>

    <!-- Log -->
    <a-divider />
    <b>{{ $t("all.result") }}</b>
    <div class="logging-wrapper">
      <a-list
        item-layout="horizontal"
        size="small"
        :data-source="search_result"
      >
        <a-list-item slot="renderItem" slot-scope="item">
          <div v-if="item.type=='file'" slot="actions">
            <a-icon type="file-search" @click="goto(item.dir, item.id, item.id)" />
            <a-divider type="vertical" />
            <a-icon type="folder-open" @click="goto(item.dir, item.id)" />
          </div>
          <div v-if="item.type=='dir'" slot="actions">
            <a-icon type="folder-open" @click="goto(item.id)" />
          </div>
          <span>{{ item.name }}{{ item.ext }}</span>
        </a-list-item>
      </a-list>
    </div>
  </div>
</template>

<script>
import { http_post } from "@/util/HttpRequest";
import ArtonWebsocket from "@/util/ArtonWebsocket";

export default {
  data() {
    return {
      form: this.$form.createForm(this, { name: "advanced_search" }),
      mode: "file",
      search_result: [],
      searching: false,
    };
  },
  beforeMount() {
    const vm = this;
    vm.explorer = vm.$store.state.explorer;
    vm.repository = vm.$store.state.repository;
    vm.setting = vm.$store.state.setting;

    // Websocket
    vm.websocket = new ArtonWebsocket();
    vm.websocket.onMessage = (message) => {
      if (message.data) {
        const msg = JSON.parse(message.data);
        switch (msg?.type) {
          default:
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
    vm.websocket.connect(`ws://${vm.setting.address}/searchfile`);

    let nocache = vm.explorer.nocache;
    if (nocache && nocache.search_result) {
      vm.search_result = nocache.search_result;
    }
  },
  beforeDestroy() {
    const vm = this;
    vm.websocket?.close();
  },
  methods: {
    /* * * * * * * * Start: Trigger * * * * * * * */
    goto(current, selected, filter) {
      const vm = this;
      vm.$router.push({
        name: "Explorer",
        query: {
          current,
          selected,
          filter,
        },
      });
    },
    handleReset() {
      this.form.resetFields();
    },
    handleSearch(e) {
      e.preventDefault();

      const vm = this;
      vm.form.validateFields((error, values) => {
        if (error) {
          console.log(`[Error] form error ${error}`);
          return;
        }
        let empty_values = true;
        for (const k in values) {
          if (values[k]) {
            empty_values = false;
            break;
          }
        }
        if (empty_values) {
          vm.$message.error(vm.$i18n.t("all.param_invalid"));
          return;
        }
        vm.searching = true;
        vm.search_result.splice(0, vm.search_result.length);

        const body = {
          ...values,
          wid: vm.repository.wid,
        };
        vm.http_post(
          `http://${vm.setting.address}/searchfile/search${vm.mode}`,
          body
        )
          .then((data) => {
            for (const i in data) {
              vm.search_result.push(data[i]);
            }
            vm.searching = false;

            // update vuex
            vm.$store.commit("updateExplorerNocache", {
              search_result: vm.search_result,
            });
          })
          .catch((err) => {
            console.log(`[Error] failed to search ${vm.mode} ${err}`);
            vm.searching = false;
          });
      });
    },
    http_post(url, body) {
      return http_post(this, url, body);
    },
    /* * * * * * * * End: Trigger * * * * * * * */
  },
};
</script>

<style scoped>
.ant-advanced-search-form {
  padding: 10px 24px;
  background: #fbfbfb;
  border: 1px solid #d9d9d9;
  border-radius: 6px;
}

.logging-wrapper {
  min-height: 50px;
  max-height: calc(100vh - 350px);
  overflow: auto;
}
</style>

<style>
.ant-advanced-search-form .ant-form-item {
  display: flex;
}

.ant-advanced-search-form .ant-form-item-control-wrapper {
  flex: 1;
}
</style>
