#pragma once

#include <rex/rex_app.h>

class MushiApp : public rex::ReXApp {
 public:
  using rex::ReXApp::ReXApp;

  static std::unique_ptr<rex::ui::WindowedApp> Create(rex::ui::WindowedAppContext& ctx) {
    return std::unique_ptr<MushiApp>(new MushiApp(ctx, "mushi", PPCImageConfig));
  }

  void OnPreSetup(rex::RuntimeConfig& config) override {
    if (config.gpu_plugin.empty()) {
      config.gpu_plugin = "xenos";
    }
  }

  void OnPostSetup() override {
    window()->SetTitle("Mushihimesama Futari");

    auto keybind_default = [](const char* name, const char* value) {
      if (rex::cvar::GetFlagSource(name) == rex::cvar::Source::kDefault) {
        rex::cvar::SetFlagByName(name, value);
      }
    };
    keybind_default("mnk_mode", "true");
    keybind_default("keybind_a", "Z");
    keybind_default("keybind_b", "X");
    keybind_default("keybind_x", "Tab");
    keybind_default("keybind_right_trigger", "Shift");
    keybind_default("keybind_lstick_up", "Up");
    keybind_default("keybind_lstick_down", "Down");
    keybind_default("keybind_lstick_left", "Left");
    keybind_default("keybind_lstick_right", "Right");
    keybind_default("keybind_rstick_up", "W");
    keybind_default("keybind_rstick_down", "S");
    keybind_default("keybind_rstick_left", "A");
    keybind_default("keybind_rstick_right", "D");
    keybind_default("keybind_start", "Return,Escape");
  }
};
