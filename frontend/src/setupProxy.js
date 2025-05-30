const { createProxyMiddleware } = require("http-proxy-middleware");

module.exports = function (app) {
  app.use(
    ["/api"],
    createProxyMiddleware({
      target: "http://127.0.0.1:5000",
      changeOrigin: true,
      pathRewrite: {
        "^/api/": "/",
      },
    })
  );

  // app.use(
  //   ["/config.js"],
  //   createProxyMiddleware({
  //     target: "http://localhost:5000",
  //     changeOrigin: true,
  //     pathRewrite: {
  //       "^/api": "/",
  //     },
  //   })
  // );

  // app.use(
  //   ['/worker'],
  //   createProxyMiddleware({
  //     target: 'http://localhost:5001',
  //     changeOrigin: true,
  //     pathRewrite: {
  //       '^/worker/': '/',
  //     },
  //   })
  // );
};
