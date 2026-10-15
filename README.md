# Mushihimesama Futari Recompilation

Mushihimesama Futari (Xbox 360) recompilation using [ReXGlue](https://github.com/rexglue/rexglue-sdk). <sup>(not vibecoded 🤯)</sup>

## Building

1. Make sure you have all [ReXGlue prerequisites](https://github.com/rexglue/rexglue-sdk/wiki/Getting-Started#prerequisites).

2. Clone the repository and build ReXGlue:

```sh
git clone --recurse-submodules https://github.com/chip44/mushi-futari-recomp
cd mushi-futari-recomp

# apply patches
cd thirdparty/rexglue-sdk
git am ../../patches/*.patch

cd -
```

3. Grab the [ISO](https://archive.org/download/mushihimesama-futari-ver.-1.5-rf/Mushihimesama%20Futari%20Ver.%201.5%20%5BRF%5D.iso), extract it using [xdvdfs](https://github.com/antangelo/xdvdfs) and put it into `game/` (entrypoint at `game/default.xex`).

4. Recompile and run:

```sh
# configure
cmake --preset linux-amd64-release

# codegen
cmake --build --preset linux-amd64-release --target mushi_codegen

# build
cmake --build --preset linux-amd64-release

# run
./out/build/linux-amd64-release/Mushihimesama\ Futari --game_data_root=game --config mushi.toml
```

## Configuration

Edit `mushi.toml` to change config values.

Press `F4` ingame to open the settings overlay with all available options.

### Default keybindings

| Action     | Key         |
|------------|-------------|
| Movement   | Arrow keys  |
| Shot       | Z           |
| Bomb       | X           |
| Rapid shot | C           |

