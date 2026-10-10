#pragma once

#include <rex/rex_app.h>

REXCVAR_DEFINE_STRING(config, "", "App", "Path to a config TOML")
    .lifecycle(rex::cvar::Lifecycle::kInitOnly);

class MushiApp : public rex::ReXApp {
 public:
  using rex::ReXApp::ReXApp;

  static std::unique_ptr<rex::ui::WindowedApp> Create(rex::ui::WindowedAppContext& ctx) {
    return std::unique_ptr<MushiApp>(new MushiApp(ctx, "mushi", PPCImageConfig));
  }

  void OnConfigurePaths(rex::PathConfig& paths) override {
    std::string config_path = REXCVAR_GET(config);
    if (!config_path.empty()) {
      paths.config_path = std::filesystem::absolute(config_path);
    }
  }

  void OnPreSetup(rex::RuntimeConfig& config) override {
    if (config.gpu_plugin.empty()) {
      config.gpu_plugin = "xenos";
    }
  }

  void OnPostSetup() override {
    window()->SetTitle("Mushihimesama Futari");
  }
};
