#include <android/native_window_jni.h>
#include <jni.h>
#include <vulkan/vulkan.h>

#include <atomic>
#include <cstdint>
#include <mutex>
#include <string>

namespace {
struct EngineState {
    std::mutex mutex;
    ANativeWindow* window = nullptr;
    std::atomic<bool> initialized{false};
    std::atomic<int32_t> width{0};
    std::atomic<int32_t> height{0};
    std::atomic<uint64_t> frameSeed{0};
};

EngineState gEngine;

void releaseWindowLocked() {
    if (gEngine.window != nullptr) {
        ANativeWindow_release(gEngine.window);
        gEngine.window = nullptr;
    }
}

std::string vulkanAvailability() {
    uint32_t version = 0;
    const VkResult result = vkEnumerateInstanceVersion(&version);
    if (result != VK_SUCCESS) {
        return "Vulkan unavailable";
    }
    return "Vulkan " + std::to_string(VK_VERSION_MAJOR(version)) + "." +
           std::to_string(VK_VERSION_MINOR(version)) + "." +
           std::to_string(VK_VERSION_PATCH(version));
}
}  // namespace

extern "C" JNIEXPORT void JNICALL
Java_com_genesisprotocol_game_NativeGenesisEngine_initialize(JNIEnv*, jobject) {
    gEngine.initialized.store(true);
    gEngine.frameSeed.store(0x0000000000000001ULL);
}

extern "C" JNIEXPORT void JNICALL
Java_com_genesisprotocol_game_NativeGenesisEngine_attachSurface(JNIEnv* env, jobject, jobject surface) {
    std::lock_guard<std::mutex> lock(gEngine.mutex);
    releaseWindowLocked();
    gEngine.window = ANativeWindow_fromSurface(env, surface);
}

extern "C" JNIEXPORT void JNICALL
Java_com_genesisprotocol_game_NativeGenesisEngine_resize(JNIEnv*, jobject, jint width, jint height) {
    gEngine.width.store(width);
    gEngine.height.store(height);
}

extern "C" JNIEXPORT void JNICALL
Java_com_genesisprotocol_game_NativeGenesisEngine_detachSurface(JNIEnv*, jobject) {
    std::lock_guard<std::mutex> lock(gEngine.mutex);
    releaseWindowLocked();
}

extern "C" JNIEXPORT void JNICALL
Java_com_genesisprotocol_game_NativeGenesisEngine_shutdown(JNIEnv*, jobject) {
    std::lock_guard<std::mutex> lock(gEngine.mutex);
    releaseWindowLocked();
    gEngine.initialized.store(false);
}

extern "C" JNIEXPORT jstring JNICALL
Java_com_genesisprotocol_game_NativeGenesisEngine_statusLine(JNIEnv* env, jobject) {
    const std::string status = std::string(gEngine.initialized.load() ? "Engine online" : "Engine offline") +
        " | " + vulkanAvailability() +
        " | Surface " + std::to_string(gEngine.width.load()) + "x" + std::to_string(gEngine.height.load());
    return env->NewStringUTF(status.c_str());
}
