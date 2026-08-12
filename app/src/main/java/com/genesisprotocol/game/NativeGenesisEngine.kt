package com.genesisprotocol.game

import android.view.Surface

class NativeGenesisEngine {
    init {
        System.loadLibrary("genesis_engine")
    }

    external fun initialize()
    external fun attachSurface(surface: Surface)
    external fun resize(width: Int, height: Int)
    external fun detachSurface()
    external fun shutdown()
    external fun statusLine(): String
}
