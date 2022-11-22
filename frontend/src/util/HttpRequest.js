import options from "@/config/request";

function http_post(vm, url, body) {
  return new Promise((resolve, reject) => {
    vm.$http
      .post(url, body, options)
      .then(
        (resp) => {
          const data = resp.body?.data;
          if (data && resp.body?.status === "success") {
            resolve(data);
          } else {
            reject();
          }
        },
        (error) => {
          reject(error);
        }
      );
  });
}

export { http_post };
